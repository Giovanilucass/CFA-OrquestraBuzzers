import json
import unittest
from unittest.mock import patch

from podio.maestro import Maestro, TOPICO_PARTITURA


class MaestroDestinosTests(unittest.TestCase):
    def test_usa_ids_descobertos_da_sincronizacao_quando_nao_houve_destinos_hardcoded(self):
        maestro = Maestro(caminho_partituras="podio/repertorio", destinos=None)
        maestro.partituras = {
            "teste": {
                "parte_1": [["C4"]],
                "parte_2": [["D4"]],
            }
        }
        maestro.clientes_tempos = {
            "musico_01": {"t_estimado": 1000},
            "musico_02": {"t_estimado": 2000},
        }

        publicados = []

        class FakeClient:
            def publish(self, topic, payload):
                publicados.append((topic, payload))

        maestro.client = FakeClient()
        maestro.sincronizar = lambda: 5000

        with patch("podio.maestro.time.sleep", return_value=None):
            maestro.enviar_musica("teste", bpm=120)

        destinos_publicados = [
            json.loads(payload)["destino"]
            for topic, payload in publicados
            if topic == TOPICO_PARTITURA
        ]

        self.assertEqual(destinos_publicados, ["musico_01", "musico_02"])


if __name__ == "__main__":
    unittest.main()
