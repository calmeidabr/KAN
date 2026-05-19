# AGENTS.md

## Objetivo do projeto
Esta é uma aplicação Python com frontend em Streamlit.

O objetivo dos agentes neste repositório é:
- melhorar o frontend;
- melhorar a organização do código;
- melhorar a performance da navegação;
- preservar a lógica de negócio existente sempre que possível.

## Como trabalhar neste projeto
Antes de modificar arquivos:
1. analisar a estrutura atual;
2. identificar gargalos ou problemas reais;
3. propor mudanças curtas e objetivas;
4. só então editar.

Evite reescrever grandes partes do projeto sem necessidade.

## Regras gerais
- Priorize legibilidade, manutenção e simplicidade.
- Preserve o comportamento existente, salvo quando houver bug claro ou pedido explícito.
- Evite duplicação de código.
- Prefira funções curtas e nomes descritivos.
- Separe responsabilidades por arquivo ou módulo.
- Não misture lógica de negócio, layout e estado no mesmo bloco quando isso puder ser evitado.
- Ao sugerir refatoração, faça mudanças incrementais.
- Ao editar, explique rapidamente o racional técnico.

## Convenções para Streamlit
- O sidebar deve ser leve e focado em navegação, filtros e controles simples.
- Não colocar processamento pesado diretamente no sidebar.
- Evitar reruns desnecessários.
- Quando fizer sentido, usar cache para dados e recursos pesados.
- Quando fizer sentido, usar session_state para manter estado entre interações.
- Preferir componentes e blocos reutilizáveis entre páginas.
- Reduzir repetição visual entre páginas.
- Evitar criar páginas com código excessivamente acoplado.

## Frontend
Objetivos visuais:
- layout moderno, limpo e funcional;
- boa hierarquia visual;
- sidebar organizada;
- cards, seções e blocos com consistência;
- tipografia e espaçamento mais claros;
- foco em legibilidade.

Boas práticas:
- sugerir melhorias visuais antes de alterar muito a interface;
- reaproveitar padrões de layout;
- criar estruturas visuais consistentes entre páginas;
- evitar excesso de widgets e excesso de informação por tela.

## Performance
Ao investigar lentidão:
- localizar o gargalo real antes de otimizar;
- verificar se há leitura repetida de arquivos;
- verificar se há cálculos repetidos em reruns;
- verificar se há consultas, APIs ou transformações pesadas em toda interação;
- verificar se o arquivo principal executa lógica demais a cada troca de página.

## Arquitetura
Preferir organização por responsabilidade, por exemplo:
- app ou main para bootstrap e roteamento;
- pages para telas;
- services para acesso a dados e integrações;
- components ou ui para elementos visuais reutilizáveis;
- state para session_state, preferências e controle de fluxo.

## Dependências
- Não adicionar novas dependências sem necessidade.
- Se sugerir nova biblioteca, explicar a razão.
- Preferir soluções nativas ou já existentes no projeto.

## Estilo de resposta do agente
- Seja direto.
- Mostre primeiro o diagnóstico.
- Depois proponha a mudança.
- Depois implemente.
- Em mudanças grandes, divida em etapas pequenas.
- Em mudanças visuais, explicar impacto em UX e manutenção.

## Arquivos especializados
Use estes arquivos como complemento temático:
- `./agents/frontend.md`
- `./agents/streamlit-performance.md`
- `./agents/architecture.md`