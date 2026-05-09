# Schema das Fontes de Dados — EdTech Lakehouse GCP (LearnHub)

Documentação dos schemas das 21 entidades da plataforma fictícia **LearnHub**.
Todos os dados são sintéticos, gerados com Faker, baseados na lógica de negócio de uma plataforma EdTech real.

> **Chave central:** `userId` (UUID v4) — presente em todas as collections de comportamento, engajamento, scores e financeiro.

---

## Sumário

| Domínio | Collections | Estratégia |
|---|---|---|
| [Usuários](#1-usuários) | `users`, `userprofiles`, `userplans` | WRITE_TRUNCATE / SCD2 |
| [Conteúdo](#2-conteúdo) | `courses`, `events`, `plans` | WRITE_TRUNCATE |
| [Engajamento](#3-engajamento) | `usercourseprogresses`, `usercourseprogresssummarizeds`, `newusereventprogresses`, `audittraffics` | MERGE / WRITE_TRUNCATE / WRITE_APPEND |
| [Scores](#4-scores) | `scores`, `scoresummarizeds` | WRITE_APPEND / WRITE_TRUNCATE |
| [Financeiro](#5-financeiro) | `subscriptions`, `bills`, `consolidated_sales` | SCD2 / WRITE_TRUNCATE |
| [Social](#6-social) | `comments`, `likes` | WRITE_APPEND |
| [Certificações](#7-certificações) | `certificates`, `specialization_graduates` | WRITE_APPEND |
| [CRM / Pagamentos](#8-crm--pagamentos) | `gateway_customers`, `crm_contacts` | WRITE_TRUNCATE / Checkpoint |

---

## 1. Usuários

### `users`
Registro principal do usuário na plataforma. Criado no momento do cadastro.

| Campo | Tipo | Descrição |
|---|---|---|
| `userId` | string (UUID) | **PK** — identificador único do usuário |
| `name` | string | Primeiro nome |
| `lastName` | string | Sobrenome |
| `email` | string | E-mail de acesso |
| `phoneNumber` | string | Telefone (formato E.164 sem +) |
| `LHID` | string | ID interno legível (ex: LH20422975) |
| `active` | boolean | Usuário ativo na plataforma |
| `profile` | string | Perfil de compra: `B2C`, `B2B` |
| `company` | string | Empresa do usuário |
| `companySize` | string | Tamanho: `1-10`, `11-50`, `51-200`, `201-500`, `500+` |
| `acceptedCommunication` | boolean | Aceite de comunicação de marketing |
| `acceptedTerms` | boolean | Aceite dos termos de uso |
| `isForeign` | boolean | Indica usuário estrangeiro |
| `experienceTime` | string | Tempo de experiência na área |
| `carreerStage` | string | Momento de carreira |
| `createdAt` | datetime | Data de criação do cadastro |

**Estratégia:** WRITE_TRUNCATE | **Relacionamentos:** `userId` → todas as demais collections

---

### `userprofiles`
Perfil detalhado do usuário.

| Campo | Tipo | Descrição |
|---|---|---|
| `userId` | string (UUID) | **FK** → `users.userId` |
| `personal_data` | object | `about.full_name`, `about.phone_number`, `about.goal` |
| `professional_data` | object | `career_moment`, `professional_experience.current_role` |
| `formation` | object | `academic_formation.list`, `skills.list` |

**Estratégia:** WRITE_TRUNCATE

---

### `userplans`
Plano ativo do usuário. Atualizado a cada mudança de plano ou renovação.

| Campo | Tipo | Descrição |
|---|---|---|
| `userPlanId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `planId` | string (UUID) | **FK** → `plans.planId` |
| `planName` | string | Nome do plano: `Master`, `Pro`, `Plus`, `Starter` |
| `validity` | datetime | Data de expiração do plano |
| `isTrial` | boolean | Plano atual é trial |
| `trialUsed` | boolean | Trial já foi utilizado |
| `trialUseDate` | datetime | Data em que o trial foi ativado |
| `createdAt` | datetime | Data de criação |
| `updatedAt` | datetime | Data da última atualização |

**Estratégia:** SCD Tipo 2 — adiciona `valid_from`, `valid_to`, `is_current` na silver

---

## 2. Conteúdo

### `courses`
Catálogo de cursos gravados da plataforma.

| Campo | Tipo | Descrição |
|---|---|---|
| `courseId` | string (UUID) | **PK** |
| `name` | string | Nome do curso |
| `description` | string | Descrição do curso |
| `certificate` | boolean | Curso emite certificado |
| `categories` | array[string] | `CURSOS`, `MASTERCLASS` |
| `categoryGroups` | array[string] | `Customer Success`, `CX`, `Dados`, `Liderança`, `Vendas` |
| `levels` | array[string] | `1` (básico), `2` (intermediário), `3` (avançado) |
| `tags` | array[string] | Tags de busca |
| `durationHours` | integer | Duração em horas |
| `durationMinutes` | integer | Duração em minutos |
| `plans` | array[string] | Planos com acesso (FK → `plans.planId`) |
| `modules` | array[object] | `moduleId`, `order`, `title`, `topics[]` |
| `modules[].topics` | array[object] | `topicId`, `order`, `title`, `durationInSeconds` |
| `createdAt` | datetime | Data de publicação |

**Estratégia:** WRITE_TRUNCATE

---

### `events`
Catálogo de eventos ao vivo (masterclasses, especializações).

| Campo | Tipo | Descrição |
|---|---|---|
| `eventId` | string (UUID) | **PK** |
| `title` | string | Título do evento |
| `description` | string | Descrição curta |
| `category` | string | `masterclass`, `especializacao` |
| `subject` | string | `customer_experience`, `dados`, `cx`, `lideranca`, `vendas` |
| `hostName` | string | Nome do apresentador |
| `hostEmail` | string | E-mail do apresentador |
| `highlight` | boolean | Evento em destaque |
| `tags` | array[string] | Tags de busca |
| `durationHours` | integer | Duração em horas |
| `durationMinutes` | integer | Duração em minutos |

**Estratégia:** WRITE_TRUNCATE

---

### `plans`
Catálogo de planos disponíveis na plataforma LearnHub.

| Campo | Tipo | Descrição |
|---|---|---|
| `planId` | string (UUID) | **PK** |
| `name` | string | `Master`, `Pro`, `Plus`, `Starter` |
| `description` | string | Descrição do plano |
| `hierarchy` | integer | 1=Master, 2=Pro, 3=Plus, 4=Starter |
| `color` | string | Cor HEX do plano na UI |
| `trialAvailable` | boolean | Plano disponível para trial |

**Estratégia:** WRITE_TRUNCATE

---

## 3. Engajamento

### `usercourseprogresses`
Progresso do usuário em cada tópico de cada curso.

| Campo | Tipo | Descrição |
|---|---|---|
| `userCourseProgressId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `courseId` | string (UUID) | **FK** → `courses.courseId` |
| `moduleId` | string (UUID) | FK → módulo do curso |
| `topicId` | string (UUID) | FK → tópico do módulo |
| `progress` | float | Percentual de progresso no curso (0–100) |
| `videoProgress` | float | Percentual assistido do vídeo (0–100) |
| `durationInSeconds` | integer | Duração total do vídeo |
| `lastTopicViewed` | boolean | Último tópico visualizado |
| `datesViewed` | array[datetime] | Datas de acesso |
| `createdAt` | datetime | Primeira visualização |
| `updatedAt` | datetime | Última atualização |

**Estratégia:** MERGE (upsert por `userCourseProgressId`)

---

### `usercourseprogresssummarizeds`
Visão consolidada do progresso do usuário.

| Campo | Tipo | Descrição |
|---|---|---|
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userName` | string | Nome completo |
| `company` | string | Empresa |
| `planName` | string | Nome do plano atual |
| `courses` | array[string] | courseIds acessados |
| `events` | array[object] | Eventos assistidos |
| `totalWatchedTimeInMinutes` | float | Total de minutos assistidos |
| `totalWatchedTimeCurrentMonthInMinutes` | float | Minutos no mês atual |
| `userSince` | datetime | Data de criação do usuário |
| `updatedAt` | datetime | Data da última atualização |

**Estratégia:** WRITE_TRUNCATE

---

### `newusereventprogresses`
Progresso do usuário em eventos ao vivo.

| Campo | Tipo | Descrição |
|---|---|---|
| `eventProgressId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userEmail` | string | E-mail do usuário |
| `userName` | string | Nome do usuário |
| `userPlanId` | string (UUID) | **FK** → `plans.planId` |
| `userPlanName` | string | Nome do plano |
| `eventId` | string (UUID) | **FK** → `events.eventId` |
| `eventName` | string | Nome do evento |
| `eventCategory` | string | `masterclass`, `especializacao` |
| `eventDate` | datetime | Data/hora do evento |
| `progress` | integer | Percentual de presença (0–100) |

**Estratégia:** WRITE_APPEND

---

### `audittraffics`
Log de navegação do usuário na plataforma.

| Campo | Tipo | Descrição |
|---|---|---|
| `auditId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `tag` | string | `login`, `course_view`, `event_view`, `certificate`, `profile`, `community` |
| `route` | string | Rota acessada |
| `createdAt` | datetime | Timestamp do acesso |

**Estratégia:** WRITE_APPEND

---

## 4. Scores

### `scores`
Eventos individuais de pontuação.

| Campo | Tipo | Descrição |
|---|---|---|
| `scoreId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `type` | integer | Tipo da ação: 1=course_started, 2=topic_completed, 3=course_completed, 4=event_attended, 5=comment_posted, 6=login, 7=certificate |
| `score` | integer | Pontuação: 10, 5, 50, 20, 5, 2, 100 |
| `active` | boolean | Score ativo |
| `entityUniqueIds` | array[string] | IDs das entidades relacionadas |
| `createdAt` | datetime | Data do evento |

**Estratégia:** WRITE_APPEND

---

### `scoresummarizeds`
Score total consolidado por usuário.

| Campo | Tipo | Descrição |
|---|---|---|
| `scoreSummarizedId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `score` | integer | Score total acumulado |
| `updatedAt` | datetime | Data da última consolidação |

**Estratégia:** WRITE_TRUNCATE

---

## 5. Financeiro

### `subscriptions`
Assinaturas dos usuários no gateway de pagamento.

| Campo | Tipo | Descrição |
|---|---|---|
| `subscriptionId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `status` | string | `active`, `future`, `canceled`, `suspended` |
| `planId` | string (UUID) | **FK** → `plans.planId` |
| `planName` | string | Nome do plano |
| `interval` | string | `months` |
| `installments` | integer | Parcelas por cobrança: 1, 6, 12 |
| `start_at` | datetime | Início da assinatura |
| `end_at` | datetime | Fim da assinatura |
| `next_billing_at` | datetime | Próxima cobrança |
| `cancel_at` | datetime | Data de cancelamento |
| `created_at` | datetime | Data de criação |
| `updated_at` | datetime | Data de atualização |

**Estratégia:** SCD Tipo 2

---

### `bills`
Cobranças geradas por ciclo de assinatura.

| Campo | Tipo | Descrição |
|---|---|---|
| `billId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `subscriptionId` | string (UUID) | **FK** → `subscriptions.subscriptionId` |
| `amount` | float | Valor cobrado (em reais) |
| `status` | string | `paid`, `pending`, `canceled` |
| `installments` | integer | Número de parcelas |
| `due_at` | datetime | Data de vencimento |
| `created_at` | datetime | Data de criação |
| `updated_at` | datetime | Data de atualização |

**Estratégia:** WRITE_TRUNCATE

---

### `consolidated_sales`
View consolidada de vendas.

| Campo | Tipo | Descrição |
|---|---|---|
| `saleId` | string (UUID) | **PK** |
| `bill_id` | string (UUID) | **FK** → `bills.billId` |
| `UserId` | string (UUID) | **FK** → `users.userId` |
| `Status` | string | Status do pagamento |
| `Vencimento` | datetime | Data de vencimento |
| `Data_Pagamento` | datetime | Data do pagamento |
| `Forma_de_Pagamento` | string | `Cartão de crédito`, `Boleto`, `Pix` |
| `Tentativas_Pagamento` | integer | Número de tentativas |
| `Nome_Produto` | string | Ex: `LearnHub Plus - Recorrência` |
| `Valor` | integer | Valor pago |
| `Valor_Total` | integer | Valor total do contrato |
| `Plano` | string | Nome do plano |
| `Categoria_Produto` | string | `Master`, `Pro`, `Plus`, `Starter` |
| `Perfil` | string | `B2C`, `B2B` |
| `Condicao_Pagamento` | string | `Recorrência`, `À vista`, `Parcelado` |
| `Numero_Parcelas` | integer | Número de parcelas |
| `Tipo_Venda` | string | `Nova Venda`, `Ciclo N - Rec`, `Upgrade` |
| `Usuario_Ativo` | boolean | Usuário ativo |
| `Data_Atualizacao` | datetime | Data de atualização |

**Estratégia:** WRITE_TRUNCATE

---

## 6. Social

### `comments`
Comentários dos usuários nos posts da comunidade.

| Campo | Tipo | Descrição |
|---|---|---|
| `commentId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userName` | string | Nome do usuário |
| `userEmail` | string | E-mail do usuário |
| `planId` | string (UUID) | **FK** → `plans.planId` |
| `postId` | string (UUID) | ID do post comentado |
| `parentCommentId` | string | ID do comentário pai (respostas) |
| `comment` | string | Conteúdo do comentário |
| `likes` | integer | Total de likes |
| `totalComments` | integer | Total de respostas |
| `createdAt` | datetime | Data do comentário |

**Estratégia:** WRITE_APPEND

---

### `likes`
Likes de usuários em posts e comentários.

| Campo | Tipo | Descrição |
|---|---|---|
| `likeId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `postId` | string (UUID) | ID do post curtido |
| `commentId` | string | ID do comentário curtido |
| `createdAt` | datetime | Data do like |

**Estratégia:** WRITE_APPEND

---

## 7. Certificações

### `certificates`
Certificados emitidos ao concluir cursos.

| Campo | Tipo | Descrição |
|---|---|---|
| `certificateId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userName` | string | Nome do usuário |
| `courseId` | string (UUID) | **FK** → `courses.courseId` |
| `courseName` | string | Nome do curso |
| `finalProgress` | float | Progresso final (%) |
| `durationHours` | integer | Duração do curso em horas |
| `durationMinutes` | integer | Duração em minutos |
| `fileName` | string | Nome do arquivo PDF |
| `finishDate` | datetime | Data de conclusão |

**Estratégia:** WRITE_APPEND

---

### `specialization_graduates`
Usuários aprovados em especializações.

| Campo | Tipo | Descrição |
|---|---|---|
| `aprovadoId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `userEmail` | string | E-mail do usuário |
| `userName` | string | Nome do usuário |
| `userPlanName` | string | Plano no momento da aprovação |
| `eventId` | string (UUID) | **FK** → `events.eventId` |
| `eventTitle` | string | Título da especialização |
| `average_progress` | float | Média de presença (%) |
| `start_time` | datetime | Data de início da especialização |

**Estratégia:** WRITE_APPEND

---

## 8. CRM / Pagamentos

### `gateway_customers`
Cadastro de clientes no gateway de pagamento. Agnóstico à ferramenta.

| Campo | Tipo | Descrição |
|---|---|---|
| `customerId` | string (UUID) | **PK** |
| `userId` | string (UUID) | **FK** → `users.userId` |
| `name` | string | Nome do cliente |
| `email` | string | E-mail |
| `registry_code` | string | CPF |
| `status` | string | `active`, `inactive` |
| `address` | object | `street`, `number`, `zipcode`, `city`, `state`, `country` |
| `phones` | array[object] | `phone_type`, `number` |
| `created_at` | datetime | Data de criação |

**Estratégia:** WRITE_TRUNCATE

---

### `crm_contacts`
Contatos extraídos do CRM. Ingestão incremental. Agnóstico à ferramenta. Armazenado em `crm/contacts/` no GCS.

| Campo | Tipo | Descrição |
|---|---|---|
| `hubspot_id` | string | **PK** — ID do contato no CRM |
| `email` | string | E-mail do contato |
| `firstname` | string | Primeiro nome |
| `lastname` | string | Sobrenome |
| `phone` | string | Telefone |
| `company` | string | Empresa |
| `jobtitle` | string | Cargo |
| `perfil_do_lead` | string | `B2B`, `B2C`, `Desconhecido` |
| `seu_cargo` | string | `CS`, `CX`, `Liderança`, `Analista`, `Buscando Recolocação` |
| `tamanho_da_empresa` | string | Porte da empresa |
| `hubspot_owner_id` | string | ID do responsável |
| `userid` | string | **FK** → `users.userId` |
| `data_inicio_trial` | datetime | Início do trial |
| `trial_cancel` | boolean | Trial cancelado |
| `trial_cancel_date` | datetime | Data de cancelamento |
| `trial_business` | string | Motivo de cancelamento B2B |
| `trial_user` | string | Motivo de cancelamento B2C |
| `lastmodifieddate` | datetime | Usado como checkpoint de ingestão |
| `_ingest_date` | date | Data da ingestão |
| `_source` | string | `crm` |

**Estratégia:** Checkpoint incremental por `lastmodifieddate` — MERGE no BigQuery

---

## Relacionamentos entre domínios

```
users (userId)
  ├── userprofiles        (userId)
  ├── userplans           (userId) → plans (planId)
  ├── usercourseprogresses (userId) → courses (courseId)
  ├── usercourseprogresssummarizeds (userId)
  ├── newusereventprogresses (userId) → events (eventId)
  ├── audittraffics       (userId)
  ├── scores              (userId)
  ├── scoresummarizeds    (userId)
  ├── comments            (userId)
  ├── likes               (userId)
  ├── certificates        (userId) → courses (courseId)
  ├── specialization_graduates (userId) → events (eventId)
  ├── consolidated_sales  (UserId) → bills (billId)
  ├── gateway_customers   (userId)
  └── crm_contacts        (userid)

subscriptions (userId) → bills (subscriptionId)
```

---

*Schema gerado com base em dados de produção anonimizados. Todos os valores são sintéticos.*
