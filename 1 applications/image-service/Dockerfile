# ---- Builder Stage ----
FROM node:18-alpine AS builder

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

# ---- Production Stage ----
FROM node:18-alpine

WORKDIR /usr/src/app

# Create a non-root user and group
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home --disabled-password appuser

COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/src ./src
COPY --from=builder /usr/src/app/package.json ./package.json

# Create a directory for the service account key and an empty placeholder file.
# This prevents issues with volume mounts where the target file must exist.
RUN mkdir -p /etc/gcp/keys && \
    touch /etc/gcp/keys/gcs-sa-key.json && \
    chown -R appuser:appgroup /etc/gcp/keys

# Change the owner of the app directory
RUN chown -R appuser:appgroup /usr/src/app

USER appuser

CMD [ "npm", "start" ]
