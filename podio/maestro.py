import json
import time
from pathlib import Path
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORTA = 1883

TOPICO_PARTITURA = "projeto/orquestra/partitura"
TOPICO_COMANDO = "projeto/orquestra/comando"
TOPICO_SYNC_REQ = "projeto/orquestra/sync/req"
TOPICO_SYNC_RES = "projeto/orquestra/sync/res"
TOPICO_SYNC_ADJ = "projeto/orquestra/sync/adj"


class Maestro:
    def __init__(self, broker=BROKER, porta=PORTA, caminho_partituras=None, destinos=None):
        self.broker = broker
        self.porta = porta
        self.caminho_partituras = self._resolver_caminho_partituras(caminho_partituras)
        self.partituras = {}
        self.client = None
        self.conectado = False
        self.clientes_tempos = {}
        self.destinos = list(destinos or [])

    def _resolver_caminho_partituras(self, caminho_partituras):
        if caminho_partituras is None:
            return Path(__file__).resolve().parent / "repertorio"

        caminho = Path(caminho_partituras).expanduser()
        if not caminho.is_absolute():
            caminho = (Path(__file__).resolve().parent / caminho).resolve()
        return caminho

    def _carregar_partitura_do_arquivo(self, caminho):
        print(f"Lendo a partitura do arquivo '{caminho}'...")
        try:
            with caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"ERRO: Arquivo '{caminho}' não encontrado.")
            return {}
        except ValueError:
            print("ERRO: O arquivo possui JSON inválido.")
            return {}

        if isinstance(dados, dict):
            return {caminho.stem: dados}

        if isinstance(dados, list):
            return {caminho.stem: dados}

        print(f"ERRO: O conteúdo de '{caminho}' não é uma partitura válida.")
        return {}

    def ler_partituras_do_arquivo(self):
        caminho = self.caminho_partituras
        if not caminho.exists():
            print(f"ERRO: Caminho '{caminho}' não encontrado.")
            self.partituras = {}
            return {}

        if caminho.is_dir():
            print(f"Lendo as partituras da pasta '{caminho}'...")
            partituras = {}
            for arquivo_json in sorted(caminho.glob("*.json")):
                partituras.update(self._carregar_partitura_do_arquivo(arquivo_json))
            self.partituras = partituras
            return self.partituras

        self.partituras = self._carregar_partitura_do_arquivo(caminho)
        return self.partituras

    def listar_musicas(self):
        if not self.partituras:
            self.ler_partituras_do_arquivo()
        return sorted(self.partituras.keys())

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self.conectado = True
            print(f"Conectado ao broker MQTT ({self.broker}:{self.porta}).")
        else:
            print(f"Falha ao conectar ao broker MQTT. Código: {reason_code}")

    def _on_message(self, client, userdata, msg):
        if msg.topic != TOPICO_SYNC_RES:
            return

        try:
            dados = json.loads(msg.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            print("Resposta de sincronização inválida recebida.")
            return

        cliente_id = dados.get("id")
        if cliente_id:
            self.clientes_tempos[cliente_id] = {
                "t_cliente": dados.get("t", 0),
                "t_recebido_ms": int(time.time() * 1000),
            }
            print(f"Resposta de sincronização recebida de '{cliente_id}'.")

    def _resolver_destino_para_parte(self, indice):
        if self.destinos and indice < len(self.destinos):
            return self.destinos[indice]

        clientes_descobertos = list(self.clientes_tempos.keys())
        if indice < len(clientes_descobertos):
            return clientes_descobertos[indice]

        return None

    def conectar(self):
        if mqtt is None:
            raise RuntimeError("A biblioteca paho-mqtt não está instalada.")

        print(f"Conectando ao Broker MQTT ({self.broker}:{self.porta})...")
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except (AttributeError, TypeError):
            self.client = mqtt.Client()

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(self.broker, self.porta, 60)
        self.client.subscribe(TOPICO_SYNC_RES)
        self.client.loop_start()

        while not self.conectado:
            time.sleep(0.1)

    def sincronizar(self):
        if self.client is None:
            raise RuntimeError("O maestro ainda não está conectado ao MQTT.")

        self.clientes_tempos.clear()
        print("Iniciando algoritmo de Berkeley...")
        t_req_ms = int(time.time() * 1000)
        self.client.publish(TOPICO_SYNC_REQ, "SYNC")

        print("Aguardando respostas dos músicos...")
        time.sleep(10)

        t_agora_ms = int(time.time() * 1000)
        tempos_estimados = [t_agora_ms]

        for cid, dados in self.clientes_tempos.items():
            rtt = dados["t_recebido_ms"] - t_req_ms
            t_estimado = dados["t_cliente"] + (rtt / 2) + (t_agora_ms - dados["t_recebido_ms"])
            dados["t_estimado"] = t_estimado
            tempos_estimados.append(t_estimado)

        if self.clientes_tempos:
            tempo_medio = sum(tempos_estimados) / len(tempos_estimados)
            print(f"Tempo global calculado. Sincronizando {len(self.clientes_tempos)} músicos...")
        else:
            tempo_medio = t_agora_ms
            print("Nenhum músico respondeu. Usando o tempo local do maestro.")

        for cid, dados in self.clientes_tempos.items():
            print("Publicando SYNC_ADJ para", cid)
            offset = tempo_medio - dados["t_estimado"]
            payload = json.dumps({"id": cid, "offset_ms": int(offset)})
            self.client.publish(TOPICO_SYNC_ADJ, payload)

        time.sleep(1)
        return int(tempo_medio)

    def enviar_musica(self, nome_musica, bpm=140):
        if nome_musica not in self.partituras:
            print(f"Música '{nome_musica}' não encontrada.")
            return

        tempo_global = self.sincronizar()
        partitura = self.partituras[nome_musica]

        if isinstance(partitura, dict) and partitura:
            partes = list(partitura.items())
            print(f"Enviando '{nome_musica}' em {len(partes)} partes...")
            for indice, (nome_parte, trecho) in enumerate(partes):
                destino = self._resolver_destino_para_parte(indice)
                pacote = {
                    "bpm": bpm,
                    "musica": nome_musica,
                    "parte": nome_parte,
                    "partes_totais": len(partes),
                    "destino": destino,
                    "partitura": trecho,
                }
                payload_json = json.dumps(pacote)
                destino_texto = destino or "todos"
                print(f"  -> Parte '{nome_parte}' enviada para '{destino_texto}'.")
                self.client.publish(TOPICO_PARTITURA, payload_json)
                time.sleep(1)
        else:
            pacote = {
                "bpm": bpm,
                "musica": nome_musica,
                "parte": "principal",
                "partes_totais": 1,
                "destino": None,
                "partitura": partitura,
            }
            payload_json = json.dumps(pacote)
            print(f"Enviando '{nome_musica}' no tópico '{TOPICO_PARTITURA}'...")
            self.client.publish(TOPICO_PARTITURA, payload_json)
            time.sleep(1)

        start_at = int(tempo_global + 5000)
        comando = json.dumps({"comando": "START", "start_at": start_at})
        print(f"Comando enviado! A música começará em {start_at}.")
        self.client.publish(TOPICO_COMANDO, comando)

    def executar(self):
        self.ler_partituras_do_arquivo()
        self.conectar()

        print("Maestro online. Digite 's' para sair.")
        while True:
            musicas = self.listar_musicas()
            print("\nMúsicas disponíveis:")
            for indice, nome in enumerate(musicas, start=1):
                print(f"  {indice}. {nome}")

            escolha = input("Escolha o número da música: ").strip().lower()
            if escolha in {"s", "q", "quit", "exit"}:
                break

            try:
                indice = int(escolha) - 1
            except ValueError:
                print("Escolha inválida. Digite um número ou 's' para sair.")
                continue

            if 0 <= indice < len(musicas):
                nome_musica = musicas[indice]
                bpm_texto = input("BPM [140]: ").strip() or "140"
                try:
                    bpm = int(bpm_texto)
                except ValueError:
                    print("BPM inválido. Usando 140.")
                    bpm = 140
                self.enviar_musica(nome_musica, bpm)
            else:
                print("Escolha fora da lista.")

        self.encerrar()

    def encerrar(self):
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
        print("Maestro encerrado.")


if __name__ == "__main__":
    maestro = Maestro()
    maestro.executar()