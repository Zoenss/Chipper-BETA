"""Orientações conservadoras de logística reversa por material, sem afirmar recuperação."""
from __future__ import annotations

DESTINOS = {
    "Ouro": "Encaminhe placas e contatos eletrônicos a recicladores especializados; não tente extração química doméstica.",
    "Prata": "Encaminhe placas e contatos a recicladores especializados; não faça refino doméstico.",
    "Paládio": "Encaminhe placas a instalações especializadas; não use ácidos ou queimadas.",
    "Cobre": "Segregue cabos e peças metálicas quando houver separação segura; entregue a recicladores de metais.",
    "Alumínio": "Separe carcaças e peças de alumínio quando possível e entregue a recicladores licenciados.",
    "Ferro e aço": "Separe estruturas e peças ferrosas quando seguro; destine a reciclagem de metais.",
    "Estanho": "Encaminhe soldas e placas eletrônicas a processamento especializado; evite aquecimento informal.",
    "Níquel": "Encaminhe baterias e frações contendo níquel a operador especializado; não abra células.",
    "Cobalto": "Encaminhe baterias a pontos de coleta e operadores especializados; não abra, perfure ou descarregue células manualmente.",
    "Lítio": "Priorize coleta especializada de baterias; isole unidades danificadas, sem perfurar ou desmontar.",
    "Silício": "Mantenha chips e placas na fração eletrônica destinada a recicladores especializados.",
    "Vidro": "Vidros de telas não devem ser tratados automaticamente como vidro de embalagem; encaminhe com a fração eletrônica.",
    "Plásticos": "Separe plásticos eletrônicos apenas quando houver identificação e rota de reciclagem adequada; evite queima.",
    "Outros materiais": "Composição não especificada: mantenha identificado e encaminhe a operador habilitado para triagem.",
}


def orientar_materiais(materiais: list[dict]) -> list[dict[str, str]]:
    """A categoria material é estimada; rota real depende de triagem e coleta local."""
    resultado = []
    for item in materiais:
        nome = str(item.get("material", "")).strip()
        if not nome:
            continue
        resultado.append({
            "material": nome,
            "orientacao": DESTINOS.get(
                nome, "Material sem rota específica cadastrada; solicite avaliação de operador especializado."
            ),
        })
    return resultado
