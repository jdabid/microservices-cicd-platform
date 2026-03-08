{{/*
Expand the name of the chart.
*/}}
{{- define "microservices-platform.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "microservices-platform.fullname" -}}
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
{{- define "microservices-platform.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "microservices-platform.labels" -}}
helm.sh/chart: {{ include "microservices-platform.chart" . }}
{{ include "microservices-platform.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: {{ include "microservices-platform.name" . }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "microservices-platform.selectorLabels" -}}
app.kubernetes.io/name: {{ include "microservices-platform.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Component labels - extends common labels with a component label
*/}}
{{- define "microservices-platform.componentLabels" -}}
{{ include "microservices-platform.labels" . }}
{{- end }}

{{/*
Namespace helper
*/}}
{{- define "microservices-platform.namespace" -}}
{{- default .Values.global.namespace .Release.Namespace }}
{{- end }}
