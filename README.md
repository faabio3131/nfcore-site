# NFCore — site institucional

Site estático em GitHub Pages para **https://nfcore.com.br**.

## Rotas
- `index.html`: motor fiscal, documentos, IA, segurança, cobertura e planos;
- `core-cognitivo.html`: Core Cognitivo e Sentinela Normativo;
- `reforma-tributaria.html`: guia informativo da reforma tributária;
- `contato.html`: comercial, engenharia e portal de cliente.

A estrutura utiliza links relativos, `.nojekyll` e `CNAME` no raiz, sem SPA e sem roteamento por servidor. O CSS compartilhado original fica em `assets/site.css`, enquanto os ajustes NFCore Enterprise ficam isolados em `assets/enterprise.css`.

## Portais e atendimento
- Portal: https://app.nfcore.com.br/
- WhatsApp: +55 11 97835-0851
- E-mail: comercial@fmtecnologiaia.com.br

Planos oficiais mensais: Starter R$ 99 (300 notas), Pro R$ 249 (1.500 notas), Business R$ 590 (6.000 notas) e Enterprise R$ 1.490 (25.000 notas). A contratação é **assistida**, sem checkout simulado. O site não altera billing, gateway, credenciais, emissão ou regras fiscais de produção.

## Testes
```bash
python -m unittest discover -s tests -p "test_*.py" -v
node --check assets/site.js
python scripts/visual_smoke.py  # opcional: exige Playwright + Chrome; testa 24 cenários
```

O CI `NFCore Site Quality` executa validação offline de rotas, links, CTAs, conteúdo e sintaxe JavaScript. O teste visual cobre as quatro páginas nas larguras de 320, 375, 768, 1024, 1440 e 1920 pixels.

## Evidência técnica e limites do conteúdo
O backend `faabio3131/nf-core-v001` inclui o `EncryptedA1Vault`, com AES-256-GCM e AAD vinculado a escopo, e um Sentinela Normativo de integridade offline. O cofre inspecionado restringe o cadastro A1 a homologação. A política de roteamento multimodelo é consultiva: não comprova, sozinha, conexão Gemini 3.8 Flash em produção. Estados e municípios dependem de homologação por documento, credencial, ambiente e jurisdição. Nenhum elemento do site deve ser usado como certificado de homologação externa.

## Atenção: origem geradora
O commit base do repositório informa que essas páginas foram originalmente geradas com `npm run build:nfcore` no repositório **fm-site-novo**. Esta atualização foi aplicada diretamente ao site distribuído. Antes de uma futura regeneração pela origem, portar as alterações para o gerador ou preservar esta camada Enterprise, para evitar sobrescrita acidental.

## Publicação
Site público: GitHub Pages com domínio personalizado definido em `CNAME`. O merge na `main` publica os arquivos conforme a configuração ativa do Pages; verificar deploy e navegação pública após o merge.

## Revisão visual e cobertura municipal (06/11/2026)
A segunda entrega preserva as quatro páginas estáticas e incorpora:
- chip da home reduzido para **70% da largura anterior do contêiner** (redução de 30%);
- fundo roxo/neon mais intenso, três pilares diferenciadores e hover glow nos cards cognitivos;
- cinco etapas do fluxo fiscal convertidas em abas com painel de detalhes, teclado e acessibilidade ARIA;
- São Paulo: **22 municípios e códigos IBGE** copiados do catálogo versionado do backend em `src/kordena_fiscal/gateway/municipal_sp_routing.py`;
- MG/RJ/PR/MT/MS: **um município-piloto por UF** do inventário `src/kordena_fiscal/control_plane/national_priority_inventory.py`, com documentação normativa de `docs/NFV1_NAT01_PRIORITY_STATES_OFFICIAL_EVIDENCE_2026-11-05.md`.

**Classificação estrita:** `SP_MUNICIPAL_CANDIDATES` é um catálogo consultivo de onboarding, não uma lista de 22 municípios homologados. `NAT_PRIORITY_PILOTS` é um inventário de documentação pública e capacidades, não autorização de produção. Para transmitir é necessário vínculo canônico aprovado, credenciais, certificado, provider preparado e homologação de cada município/UF e contribuinte.

Os testes incluem contagem e códigos dos 22 municípios, as cinco capitais, fluxo ARIA e cenários visuais interativos em Chromium. O CSS e o JS possuem versão de cache `20261106`.

