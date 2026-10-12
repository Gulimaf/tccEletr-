import json
from pathlib import Path
from django.core.management.base import BaseCommand
from core.models import Produtos
class Command(BaseCommand):
    help = "Importa produtos do arquivo produtos.json"
    def add_arguments(self, parser):
        parser.add_argument(
            "arquivo",
            type=str,
            help="Caminho do arquivo JSON"
        )
    def handle(self, *args, **options):
        arquivo = Path(options["arquivo"])
        if not arquivo.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Arquivo não encontrado: {arquivo}"
                )
            )
            return
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao ler o JSON: {e}"
                )
            )
            return
        if not isinstance(dados, dict):
            self.stdout.write(
                self.style.ERROR("Formato do JSON inválido.")
            )
            return
        produtos = next(iter(dados.values()), [])
        if not isinstance(produtos, list):
            self.stdout.write(
                self.style.ERROR(
                    "Não foi encontrada uma lista de produtos no JSON."
                )
            )
            return
        self.stdout.write(
            f"Encontrados {len(produtos)} produtos."
        )
        criados = 0
        atualizados = 0
        erros = 0
        for item in produtos:
            try:
                codigo = int(item["CODIGO"])
                produto, criado = Produtos.objects.update_or_create(
                    codigo=codigo,
                    defaults={
                        "descricao": item.get("CATEGORIA") or "0",
                        "categoria": item.get("DESCRICAO") or "0",
                        "valor": item.get("VALOR") or 0,
                        "ativo": False,
                        "peso": item.get("PESO") or 0,
                        "altura": item.get("ALTURA") or 0,
                        "largura": item.get("LARGURA") or 0,
                        "comprimento": item.get("COMPRIMENTO") or 0,
                        "volume": item.get("VOLUME") or 0,
                        "is_sale": False,
                        "sale_value": 0,
                    }
                )
                if criado:
                    criados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Criado: {codigo} - {item.get('DESCRICAO')}"
                        )
                    )
                else:
                    atualizados += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"↻ Atualizado: {codigo} - {item.get('DESCRICAO')}"
                        )
                    )

            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Erro no produto "
                        f"{item.get('CODIGO', 'desconhecido')}: {e}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Importação finalizada!"))
        self.stdout.write(f"Criados: {criados}")
        self.stdout.write(f"Atualizados: {atualizados}")
        self.stdout.write(f"Erros: {erros}")