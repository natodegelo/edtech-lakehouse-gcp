config {
  type: "table",
  schema: "silver_dev",
  name: "silver_userprofiles",
  description: "Perfis detalhados dos usuários LearnHub",
  tags: ["silver", "users"]
}

SELECT
  userId,
  personal_data,
  professional_data,
  formation,
  CURRENT_TIMESTAMP()  AS _transformed_at,
  '1.0.0'             AS _pipeline_version
FROM ${ref("userprofiles")}
WHERE userId IS NOT NULL