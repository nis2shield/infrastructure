{{/*
Expand the name of the chart.
*/}}
{{- define "nis2shield.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "nis2shield.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nis2shield.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nis2shield.labels" -}}
helm.sh/chart: {{ include "nis2shield.chart" . }}
{{ include "nis2shield.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: nis2shield
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nis2shield.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nis2shield.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Component labels - webapp
*/}}
{{- define "nis2shield.webapp.labels" -}}
{{ include "nis2shield.labels" . }}
app.kubernetes.io/component: webapp
{{- end }}

{{- define "nis2shield.webapp.selectorLabels" -}}
{{ include "nis2shield.selectorLabels" . }}
app.kubernetes.io/component: webapp
{{- end }}

{{/*
Component labels - database
*/}}
{{- define "nis2shield.database.labels" -}}
{{ include "nis2shield.labels" . }}
app.kubernetes.io/component: database
{{- end }}

{{- define "nis2shield.database.selectorLabels" -}}
{{ include "nis2shield.selectorLabels" . }}
app.kubernetes.io/component: database
{{- end }}

{{/*
Component labels - replicator
*/}}
{{- define "nis2shield.replicator.labels" -}}
{{ include "nis2shield.labels" . }}
app.kubernetes.io/component: replicator
{{- end }}

{{- define "nis2shield.replicator.selectorLabels" -}}
{{ include "nis2shield.selectorLabels" . }}
app.kubernetes.io/component: replicator
{{- end }}

{{/*
Service account name
*/}}
{{- define "nis2shield.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "nis2shield.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database connection URL
*/}}
{{- define "nis2shield.databaseUrl" -}}
{{- if .Values.database.external.enabled }}
postgresql://{{ .Values.database.external.username }}:$(DATABASE_PASSWORD)@{{ .Values.database.external.host }}:{{ .Values.database.external.port }}/{{ .Values.database.external.database }}
{{- else }}
postgresql://{{ .Values.database.auth.username }}:$(DATABASE_PASSWORD)@{{ include "nis2shield.fullname" . }}-db:5432/{{ .Values.database.auth.database }}
{{- end }}
{{- end }}

{{/*
Security context for containers (NIS2 compliant)
*/}}
{{- define "nis2shield.securityContext" -}}
runAsNonRoot: true
runAsUser: 1000
runAsGroup: 1000
readOnlyRootFilesystem: true
allowPrivilegeEscalation: false
seccompProfile:
  type: RuntimeDefault
capabilities:
  drop:
    - ALL
{{- end }}
