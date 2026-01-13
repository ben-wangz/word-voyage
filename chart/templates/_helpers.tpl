{{/*
LLM component fullname
*/}}
{{- define "word-voyage.llm.fullname" -}}
{{- include "common.names.fullname" . }}-llm
{{- end -}}

{{/*
Frontend component fullname
*/}}
{{- define "word-voyage.frontend.fullname" -}}
{{- include "common.names.fullname" . }}-frontend
{{- end -}}

{{/*
Backend component fullname
*/}}
{{- define "word-voyage.backend.fullname" -}}
{{- include "common.names.fullname" . }}-backend
{{- end -}}

{{/*
LLM service name
*/}}
{{- define "word-voyage.llm.service.name" -}}
{{- include "word-voyage.llm.fullname" . }}
{{- end -}}

{{/*
Frontend service name
*/}}
{{- define "word-voyage.frontend.service.name" -}}
{{- include "word-voyage.frontend.fullname" . }}
{{- end -}}

{{/*
Backend service name
*/}}
{{- define "word-voyage.backend.service.name" -}}
{{- include "word-voyage.backend.fullname" . }}
{{- end -}}

{{/*
Redis host
*/}}
{{- define "word-voyage.redis.host" -}}
{{- if .Values.redis.enabled -}}
{{- include "common.names.fullname" . }}-redis-master
{{- else -}}
{{- .Values.redis.external.host -}}
{{- end -}}
{{- end -}}

{{/*
Redis port
*/}}
{{- define "word-voyage.redis.port" -}}
{{- if .Values.redis.enabled -}}
{{- .Values.redis.master.service.ports.redis -}}
{{- else -}}
{{- .Values.redis.external.port -}}
{{- end -}}
{{- end -}}

{{/*
Credentials secret name
*/}}
{{- define "word-voyage.credentials.secretName" -}}
{{- if .Values.credentials.existingSecret -}}
{{- .Values.credentials.existingSecret -}}
{{- else -}}
{{- include "common.names.fullname" . }}-credentials
{{- end -}}
{{- end -}}

{{/*
Generate JWT secret
Uses deterministic SHA256 hash for stability in ArgoCD/GitOps environments.
For production, set credentials.jwtSecret or use credentials.existingSecret.
*/}}
{{- define "word-voyage.credentials.jwtSecret" -}}
{{- if .Values.credentials.jwtSecret -}}
{{- .Values.credentials.jwtSecret -}}
{{- else -}}
{{- $seed := printf "%s-%s-jwt-secret" (include "common.names.fullname" .) .Release.Namespace -}}
{{- sha256sum $seed | trunc 48 -}}
{{- end -}}
{{- end -}}

{{/*
OpenAI Base URL (required)
*/}}
{{- define "word-voyage.credentials.openaiBaseUrl" -}}
{{- if .Values.credentials.openai.baseUrl -}}
{{- .Values.credentials.openai.baseUrl -}}
{{- else -}}
{{- fail "credentials.openai.baseUrl is required when credentials.existingSecret is not set" -}}
{{- end -}}
{{- end -}}

{{/*
OpenAI API Key (required)
*/}}
{{- define "word-voyage.credentials.openaiApiKey" -}}
{{- if .Values.credentials.openai.apiKey -}}
{{- .Values.credentials.openai.apiKey -}}
{{- else -}}
{{- fail "credentials.openai.apiKey is required when credentials.existingSecret is not set" -}}
{{- end -}}
{{- end -}}

{{/*
OpenAI Model (required)
*/}}
{{- define "word-voyage.credentials.openaiModel" -}}
{{- if .Values.credentials.openai.model -}}
{{- .Values.credentials.openai.model -}}
{{- else -}}
{{- fail "credentials.openai.model is required when credentials.existingSecret is not set" -}}
{{- end -}}
{{- end -}}
