# Schema das Fontes de Dados — EdTech Lakehouse GCP

Documentação dos schemas extraídos das fontes de produção.  
**21 fontes** | **3 origens** — MongoDB (20 collections), HubSpot API (1 endpoint), Vindi API (embutida no MongoDB)

> **Chave central:** `userId` (UUID v4) — presente em todas as collections de comportamento, engajamento, scores e financeiro. É o campo de join entre MongoDB e HubSpot.

---

## Sumário

| Domínio | Collections | Origem |
|---|---|---|
| [Usuários](#1-usuários) | `users`, `userprofiles`, `userplans` | MongoDB |
| [Conteúdo](#2-conteúdo) | `courses`, `events`, `csacademy_plans` | MongoDB |
| [Engajamento](#3-engajamento) | `usercourseprogresses`, `usercourseprogresssummarizeds`, `newusereventprogresses`, `audittraffics` | MongoDB |
| [Scores](#4-scores) | `scores`, `scoresummarizeds` | MongoDB |
| [Financeiro](#5-financeiro) | `subscriptions`, `bills`, `consolidated_sales` | MongoDB (via Vindi) |
| [Social](#6-social) | `comments`, `likes` | MongoDB |
| [Certificações](#7-certificações) | `certificates`, `aprovados_especializacao` | MongoDB |
| [CRM](#8-crm) | `customers_vindi`, `hubspot_contacts` | MongoDB (Vindi) + HubSpot API |

---

## 1. Usuários

### `users`
Registro principal do usuário na plataforma. Criado no momento do cadastro.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **PK** — identificador único do usuário |
| `name` | string | Primeiro nome |
| `lastName` | string | Sobrenome |
| `email` | string | E-mail de acesso |
| `phoneNumber` | string | Telefone (formato E.164 sem +) |
| `CSID` | string | ID interno legível (ex: CS20422975) |
| `active` | boolean | Usuário ativo na plataforma |
| `profile` | string | Perfil de compra: `B2C`, `B2B` |
| `company` | string | Empresa do usuário |
| `companySize` | string | Tamanho da empresa |
| `acceptedCommunication` | boolean | Aceite de comunicação de marketing |
| `acceptedTerms` | boolean | Aceite dos termos de uso |
| `address` | object | Endereço: `street`, `number`, `additionalDetails`, `zipcode`, `city`, `state` |
| `isForeign` | boolean | Indica usuário estrangeiro |
| `invoiceEmail` | string \| null | E-mail para nota fiscal |
| `experienceTime` | string | Tempo de experiência na área |
| `carreerStage` | string | Momento de carreira |
| `createdAt` | datetime | Data de criação do cadastro |

**Relacionamentos:** `userId` → `userprofiles`, `userplans`, `scores`, `certificates`, `comments`, `likes`, `usercourseprogresses`, `audittraffics`

---

### `userprofiles`
Perfil detalhado do usuário. Preenchido progressivamente na plataforma.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `personal_data` | object | Dados pessoais: `about.full_name`, `about.phone_number`, `about.goal` |
| `professional_data` | object | Dados profissionais: `career_moment`, `professional_experience` |
| `formation` | object | Formação: `academic_formation.list`, `skills.list` |

---

### `userplans`
Plano ativo do usuário. Atualizado a cada mudança de plano ou renovação.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `planId` | string (UUID) | **FK** → `csacademy_plans.planId` |
| `validity` | datetime | Data de expiração do plano |
| `trialUsed` | boolean | Indica se o trial foi utilizado |
| `trialUseDate` | datetime \| null | Data em que o trial foi ativado |
| `vindiSubscriptionId` | integer | **FK** → `subscriptions.id` |
| `isTrial` | boolean | Plano atual é trial |
| `accesType` | string \| null | Tipo de acesso especial |
| `createdAt` | datetime | Data de criação do registro |
| `updatedAt` | datetime | Data da última atualização |

---

## 2. Conteúdo

### `courses`
Catálogo de cursos gravados da plataforma.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `courseId` | string (UUID) | **PK** — identificador único do curso |
| `name` | string | Nome do curso |
| `description` | string | Descrição do curso |
| `certificate` | boolean | Curso emite certificado |
| `sessions` | array[string] | Seções onde aparece: `COURSES`, `BANNER`, `KEEPWATCHING` |
| `modules` | array[object] | Lista de módulos: `moduleId`, `order`, `title`, `summary`, `topics[]`, `professionals[]` |
| `modules[].topics` | array[object] | Aulas: `topicId`, `order`, `title`, `videoUrl`, `durationInSeconds` |
| `plans` | array[string] | Planos com acesso ao curso (FK → `csacademy_plans.planId`) |
| `categories` | array[string] | Categoria: `CURSOS`, `MASTERCLASS` |
| `categoryGroups` | array[string] | Grupo temático: `Customer Success`, `CX`, `Dados` |
| `levels` | array[string] | Nível: `1` (básico), `2` (intermediário), `3` (avançado) |
| `tags` | array[string] | Tags de busca |
| `durationHours` | integer | Duração em horas |
| `durationMinutes` | integer | Duração em minutos (complementar) |
| `image` | string | URL da imagem principal (SVG) |
| `imageInitCard` | string | URL da imagem card (PNG) |
| `createdAt` | datetime | Data de publicação do curso |

---

### `events`
Catálogo de eventos ao vivo (masterclasses, especializações).

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `eventId` | string (UUID) | **PK** — identificador único do evento |
| `title` | string | Título do evento |
| `description` | string | Descrição curta |
| `htmlContent` | string | Descrição completa em HTML |
| `category` | string | Tipo: `masterclass`, `especializacao` |
| `subject` | string | Tema: `customer_success`, `dados`, `cx` |
| `hostName` | string | Nome do apresentador |
| `hostEmail` | string | E-mail do apresentador |
| `coHost` | string | E-mail do co-apresentador |
| `highlight` | boolean | Evento em destaque na plataforma |
| `tags` | array[string] | Tags de busca |
| `imageUrl` | string | URL da imagem de capa |
| `durationHours` | integer | Duração em horas |
| `durationMinutes` | integer | Duração em minutos |
| `meeting` | object | Dados do Zoom: `id`, `host_email`, `start_url` |
| `modules` | array[object] | Módulos do evento (para especializações) |
| `sendNotification` | boolean | Notificação enviada aos usuários |

---

### `csacademy_plans`
Catálogo de planos disponíveis na plataforma.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `planId` | string (UUID) | **PK** — identificador único do plano |
| `name` | string | Nome do plano: `Essential`, `Specialist`, `Elite`, `Light` |
| `description` | string | Descrição curta |
| `descriptionPlan` | string | Benefícios detalhados (separados por `\|`) |
| `hierarchy` | integer | Hierarquia do plano (1 = mais alto) |
| `paymentMethods` | array[object] | Formas de pagamento: `priceId`, `amount`, `type` |
| `paymentPlans` | array[object] | Planos Vindi associados: `planId`, `type`, `isTrial` |
| `color` | string | Cor HEX do plano na UI |
| `trialAvailable` | boolean | Plano disponível para trial |

---

## 3. Engajamento

### `usercourseprogresses`
Progresso do usuário em cada tópico (aula) de cada curso. Evento granular de consumo.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userCourseProgressId` | string (UUID) | **PK** — identificador único do progresso |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `courseId` | string (UUID) | **FK** → `courses.courseId` |
| `moduleId` | string (UUID) | FK → `courses.modules.moduleId` |
| `topicId` | string (UUID) | FK → `courses.modules.topics.topicId` |
| `progress` | float | Percentual de progresso no curso (0–100) |
| `videoProgress` | float | Percentual assistido do vídeo (0–100) |
| `durationInSeconds` | integer | Duração total do vídeo em segundos |
| `lastTopicViewed` | boolean | Indica último tópico visualizado |
| `datesViewed` | array[datetime] | Datas em que o tópico foi acessado |
| `createdAt` | datetime | Primeira visualização |
| `updatedAt` | datetime | Última atualização |

---

### `usercourseprogresssummarizeds`
Visão consolidada do progresso do usuário. Atualizado periodicamente.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userName` | string | Nome completo do usuário |
| `company` | string | Empresa do usuário |
| `planName` | string | Nome do plano atual |
| `avatarUrl` | string | URL do avatar |
| `courses` | array[object] | Cursos iniciados/concluídos com progresso |
| `events` | array[object] | Eventos assistidos com progresso |
| `lastViewedCourseName` | string | Nome do último curso acessado |
| `firstViewedCourseDate` | datetime \| null | Data do primeiro acesso a conteúdo |
| `userSince` | datetime | Data de criação do usuário |
| `totalWatchedTimeInMinutes` | float | Total de minutos assistidos (histórico) |
| `totalWatchedTimeCurrentMonthInMinutes` | float | Minutos assistidos no mês atual |
| `updatedAt` | datetime | Data da última atualização |

---

### `newusereventprogresses`
Progresso do usuário em eventos ao vivo (masterclasses e especializações).

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userEmail` | string | E-mail do usuário |
| `userName` | string | Nome do usuário |
| `userPlanId` | string (UUID) | **FK** → `csacademy_plans.planId` |
| `userPlanName` | string | Nome do plano |
| `eventId` | string (UUID) | **FK** → `events.eventId` |
| `eventModuleId` | string (UUID) | FK → `events.modules.moduleId` |
| `eventZoomId` | integer | ID da sessão no Zoom |
| `eventName` | string | Nome do evento |
| `eventCategory` | string | Categoria: `masterclass`, `Especialização` |
| `eventDate` | datetime | Data/hora do evento |
| `progress` | integer | Percentual de presença (0–100) |

---

### `audittraffics`
Log de navegação do usuário na plataforma. Registra cada acesso a rotas.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `tag` | string | Ação identificada: `login`, `course_view`, `event_view`, `certificate` |
| `route` | string | Rota acessada: `/login`, `/courses/:id`, `/events/:id` |
| `createdAt` | datetime | Timestamp do acesso |

---

## 4. Scores

### `scores`
Eventos individuais de pontuação. Cada ação do usuário gera um registro.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `scoreId` | string (UUID) | **PK** — identificador único do score |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `entityUniqueIds` | array[string] | IDs das entidades relacionadas (curso, evento, tópico) |
| `type` | integer | Tipo da ação que gerou o score |
| `score` | integer | Pontuação atribuída |
| `active` | boolean | Score ativo (pode ser desativado por regra de negócio) |
| `createdAt` | datetime | Data do evento de pontuação |

---

### `scoresummarizeds`
Score total consolidado por usuário. Atualizado em batch diário.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `scoreSummarizedId` | string (UUID) | **PK** — identificador único |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `score` | integer | Score total acumulado |
| `updatedAt` | datetime | Data da última consolidação |

---

## 5. Financeiro

### `subscriptions`
Assinaturas dos usuários na Vindi. Controla o ciclo de vida do plano.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `id` | integer | **PK** — ID da assinatura na Vindi |
| `status` | string | Status: `active`, `future`, `canceled`, `suspended` |
| `start_at` | datetime | Início da assinatura |
| `end_at` | datetime \| null | Fim da assinatura (null = indefinido) |
| `next_billing_at` | datetime | Próxima cobrança |
| `overdue_since` | datetime \| null | Data de inadimplência |
| `cancel_at` | datetime \| null | Data de cancelamento |
| `interval` | string | Intervalo: `months` |
| `interval_count` | integer | Quantidade de intervalos por ciclo |
| `billing_cycles` | integer \| null | Total de ciclos (null = recorrência infinita) |
| `installments` | integer | Parcelas por cobrança |
| `customer` | object | Dados do cliente: `id`, `name`, `email` |
| `plan` | object | Plano Vindi: `id`, `name` |
| `product_items` | array[object] | Produtos da assinatura: `id`, `status`, `quantity` |
| `payment_method` | object | Forma de pagamento: `id`, `name`, `type` |
| `payment_profile` | object | Dados do cartão: `holder_name`, `card_number_last_four`, `card_expiration` |
| `current_period` | object \| null | Período atual de cobrança |
| `created_at` | datetime | Data de criação |
| `updated_at` | datetime | Data de atualização |

---

### `bills`
Cobranças geradas pela Vindi. Cada ciclo de assinatura gera uma bill.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `id` | integer | **PK** — ID da cobrança na Vindi |
| `amount` | string | Valor cobrado (em reais) |
| `status` | string | Status: `paid`, `pending`, `canceled`, `failed` |
| `installments` | integer | Número de parcelas |
| `due_at` | datetime | Data de vencimento |
| `billing_at` | datetime \| null | Data efetiva de cobrança |
| `seen_at` | datetime \| null | Data de visualização pelo cliente |
| `url` | string | Link da fatura |
| `customer` | object | Cliente: `id`, `name`, `email` |
| `subscription` | object | Assinatura: `id`, `plan.id`, `plan.name` |
| `bill_items` | array[object] | Itens cobrados: `id`, `amount`, `product_id` |
| `charges` | array[object] | Tentativas de cobrança: `id`, `amount`, `status`, `due_at`, `attempt_count` |
| `payment_profile` | object | Cartão: `holder_name`, `card_number_last_four`, `payment_company` |
| `period` | object | Período: `id`, `billing_at`, `cycle` |
| `created_at` | datetime | Data de criação |
| `updated_at` | datetime | Data de atualização |

---

### `consolidated_sales`
View consolidada de vendas, cruzando dados da Vindi com dados da plataforma.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `bill_id` | integer | **FK** → `bills.id` |
| `UserId` | string (UUID) | **FK** → `users.userId` |
| `Status` | string | Status do pagamento |
| `Vencimento` | datetime | Data de vencimento |
| `Data_Pagamento` | datetime | Data do pagamento efetivo |
| `Forma_de_Pagamento` | string | Forma: `Cartão de crédito`, `Boleto`, `Pix` |
| `Tentativas_Pagamento` | integer | Número de tentativas de cobrança |
| `Nome_Produto` | string | Nome do produto cobrado |
| `Valor` | integer | Valor pago (em reais) |
| `Valor_Total` | integer | Valor total do contrato |
| `Vendedor_Id` | string \| null | ID do vendedor responsável |
| `Nome_Vendedor` | string | Nome do vendedor |
| `Email_Usuário` | string | E-mail do usuário |
| `Nome_Usuário` | string | Nome do usuário |
| `Plano` | string | Nome do plano contratado |
| `Perfil` | string | Perfil: `B2C`, `B2B` |
| `Categoria_Produto` | string | Categoria: `Essential`, `Specialist`, `Elite`, `Light` |
| `Condicao_Pagamento` | string | Condição: `Recorrência`, `À vista`, `Parcelado` |
| `Numero_Parcelas` | integer | Número de parcelas |
| `Tipo_Venda` | string | Tipo: `Nova Venda`, `Ciclo N - Rec`, `Upgrade` |
| `Validade_Plano` | string | Data de validade do plano (DD/MM/YYYY) |
| `Usuario_Ativo` | boolean | Usuário ativo no momento da venda |
| `Email_Club_CSA` | string \| null | E-mail alternativo do clube |
| `Data_Atualizacao` | datetime | Data da última atualização do registro |

---

## 6. Social

### `comments`
Comentários dos usuários nos posts da comunidade.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `commentId` | string (UUID) | **PK** — identificador único do comentário |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userName` | string | Nome do usuário |
| `userEmail` | string | E-mail do usuário |
| `userNickName` | string | Nickname do usuário (ex: @luiz.batista) |
| `avatarUrl` | string | URL do avatar |
| `planId` | string (UUID) | **FK** → `csacademy_plans.planId` |
| `postId` | string (UUID) | ID do post comentado |
| `parentCommentId` | string \| null | ID do comentário pai (para respostas) |
| `comment` | string | Conteúdo do comentário (HTML) |
| `likes` | integer | Total de likes no comentário |
| `totalComments` | integer | Total de respostas ao comentário |
| `createdAt` | datetime | Data do comentário |

---

### `likes`
Likes de usuários em posts e comentários da comunidade.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `likeId` | string (UUID) | **PK** — identificador único do like |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `postId` | string (UUID) | ID do post curtido |
| `commentId` | string \| null | ID do comentário curtido (null se like no post) |
| `createdAt` | datetime | Data do like |

---

## 7. Certificações

### `certificates`
Certificados emitidos ao concluir cursos.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userName` | string | Nome do usuário no certificado |
| `courseId` | string (UUID) | **FK** → `courses.courseId` |
| `courseName` | string | Nome do curso |
| `finalProgress` | float | Progresso final no momento da emissão (%) |
| `durationHours` | integer | Duração do curso em horas |
| `durationMinutes` | integer | Duração em minutos |
| `fileName` | string | Nome do arquivo PDF do certificado |
| `additionalInfo` | string | Informações adicionais do certificado |
| `finishDate` | datetime | Data de conclusão e emissão |

---

### `aprovados_especializacao`
Usuários aprovados em especializações (eventos com critério de aprovação por presença).

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userEmail` | string | E-mail do usuário |
| `userName` | string | Nome do usuário |
| `userPlanName` | string | Nome do plano no momento da aprovação |
| `eventId` | string (UUID) | **FK** → `events.eventId` |
| `eventTitle` | string | Título da especialização |
| `average_progress` | float | Média de presença nas sessões (%) |
| `start_time` | datetime | Data de início da especialização |

---

## 8. CRM

### `customers_vindi`
Cadastro de clientes na Vindi (gateway de pagamento). Espelho do `users` para fins financeiros.

| Campo | Tipo | Descrição |
|---|---|---|
| `_id` | ObjectId | Identificador interno do MongoDB |
| `id` | integer | **PK** — ID do cliente na Vindi |
| `name` | string | Nome do cliente |
| `email` | string | E-mail do cliente |
| `registry_code` | string | CPF do cliente |
| `code` | string | **FK** → `users.userId` (campo de join) |
| `status` | string | Status na Vindi: `active`, `inactive` |
| `notes` | string \| null | Observações |
| `address` | object | Endereço: `street`, `number`, `zipcode`, `city`, `state`, `country` |
| `phones` | array[object] | Telefones: `phone_type`, `number` |
| `metadata` | object | Metadados extras: `email_club_csa` |
| `created_at` | datetime | Data de criação |
| `updated_at` | datetime | Data de atualização |

---

### `hubspot_contacts`
Contatos extraídos da API do HubSpot. Ingestão incremental via `lastmodifieddate`. Armazenado em GCS no formato NDJSON particionado por `ingest_date` e `ingest_time`.

| Campo | Tipo | Descrição |
|---|---|---|
| `hubspot_id` | string | **PK** — ID do contato no HubSpot |
| `email` | string | E-mail do contato |
| `firstname` | string | Primeiro nome |
| `lastname` | string \| null | Sobrenome |
| `phone` | string | Telefone |
| `company` | string \| null | Empresa |
| `jobtitle` | string \| null | Cargo |
| `perfil_do_lead` | string | Perfil: `B2B`, `B2C`, `Desconhecido` |
| `seu_cargo` | string \| null | Cargo customizado: `CS`, `CX`, `Buscando Recolocação` |
| `tamanho_da_empresa` | string \| null | Porte da empresa |
| `hubspot_owner_id` | string \| null | ID do responsável pelo contato |
| `userid` | string \| null | **FK** → `users.userId` (join com MongoDB) |
| `data_inicio_trial` | datetime \| null | Data de início do trial |
| `trial_cancel` | boolean \| null | Trial cancelado |
| `trial_cancel_date` | datetime \| null | Data de cancelamento do trial |
| `trial_business` | string \| null | Motivo de cancelamento (B2B) |
| `trial_user` | string \| null | Motivo de cancelamento (B2C) |
| `lastmodifieddate` | datetime | Data da última modificação (usado como checkpoint de ingestão) |
| `_ingest_timestamp` | datetime | Timestamp da ingestão no GCS |
| `_ingest_date` | date | Data da ingestão (partição) |
| `_source` | string | Origem do dado: `hubspot` |

---

## Relacionamentos entre domínios

```
users (userId)
  ├── userprofiles        (userId)
  ├── userplans           (userId) → csacademy_plans (planId)
  ├── usercourseprogresses (userId) → courses (courseId, moduleId, topicId)
  ├── usercourseprogresssummarizeds (userId)
  ├── newusereventprogresses (userId) → events (eventId, eventModuleId)
  ├── audittraffics       (userId)
  ├── scores              (userId)
  ├── scoresummarizeds    (userId)
  ├── comments            (userId)
  ├── likes               (userId)
  ├── certificates        (userId) → courses (courseId)
  ├── aprovados_especializacao (userId) → events (eventId)
  ├── consolidated_sales  (UserId) → bills (bill_id)
  └── hubspot_contacts    (userid) ← join via e-mail ou userId

customers_vindi (code = userId)
  └── subscriptions (customer.id) → bills (subscription.id)
```

---

*Documentação gerada com base em amostras extraídas do banco de dados de produção (MongoDB + HubSpot API + Vindi API). Os dados sintéticos do gerador respeitam este schema.*
