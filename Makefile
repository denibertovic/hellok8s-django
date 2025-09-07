.PHONY: deploy helm-template helm-diff helm-lint clean build-docker-image push-docker-image test

.DEFAULT_GOAL = help

export IMAGE_NAME = denibertovic/hellok8s-django

export PROJECT_NAME ?= hellok8s-django

export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

export CACHE_ARGS ?= "--cache-from=${IMAGE_NAME}:latest"
# export CACHE_ARGS="--no-cache"

require-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "ERROR: Environment variable not set: \"$*\""; \
		exit 1; \
	fi

## Nukes devenv and starts over
clean:
	@rm -rf .devenv
	@rm -rf .direnv
	@rm -rf node_modules

## Build docker image
build-docker-image: require-SHORT_SHA
	@docker buildx build ${CACHE_ARGS} \
	--load \
	-t "${IMAGE_NAME}:latest" \
	-t "${IMAGE_NAME}:sha-${SHORT_SHA}" .

## Push docker image
push-docker-image: require-SHORT_SHA
	@docker push "${IMAGE_NAME}:latest"
	@docker push "${IMAGE_NAME}:sha-${SHORT_SHA}"

## Deploy
deploy: require-IMAGE_TAG require-ENVIRONMENT require-NAMESPACE require-KUBECONFIG
	@# Pass .bak to -i to work on BSD/Mac and GNU/Linux sed
	@# https://unix.stackexchange.com/questions/92895/how-can-i-achieve-portability-with-sed-i-in-place-editing
	@sed -i.bak "s/^appVersion:.*$$/appVersion: ${IMAGE_TAG}/" chart/Chart.yaml
	@sops exec-file chart/values/${ENVIRONMENT}/secrets.yaml 'helm --namespace=${NAMESPACE} upgrade --install --wait ${PROJECT_NAME} chart/ \
		--values=chart/values/${ENVIRONMENT}/values.yaml \
		--values={} \
		--set image.tag=${IMAGE_TAG}'

## Uses helm-diff to show differences when upgrading
helm-diff: require-IMAGE_TAG require-ENVIRONMENT require-NAMESPACE require-KUBECONFIG
	@# Pass .bak to -i to work on BSD/Mac and GNU/Linux sed
	@# https://unix.stackexchange.com/questions/92895/how-can-i-achieve-portability-with-sed-i-in-place-editing
	@sed -i.bak "s/^appVersion:.*$$/appVersion: ${IMAGE_TAG}/" chart/Chart.yaml
	@sops exec-file chart/values/${ENVIRONMENT}/secrets.yaml 'helm --namespace=${NAMESPACE} diff --suppress-secrets --suppress ConfigMap upgrade --install ${PROJECT_NAME} chart/ \
		--values=chart/values/${ENVIRONMENT}/values.yaml \
		--values={} \
		--set image.tag=${IMAGE_TAG}'

## Uses helm lint to validate chart
helm-lint: require-IMAGE_TAG require-ENVIRONMENT require-NAMESPACE require-KUBECONFIG
	@# Pass .bak to -i to work on BSD/Mac and GNU/Linux sed
	@# https://unix.stackexchange.com/questions/92895/how-can-i-achieve-portability-with-sed-i-in-place-editing
	@sed -i.bak "s/^appVersion:.*$$/appVersion: ${IMAGE_TAG}/" chart/Chart.yaml
	@sops exec-file chart/values/${ENVIRONMENT}/secrets.yaml 'helm --namespace=${NAMESPACE} lint --quiet chart/ \
		--values=chart/values/${ENVIRONMENT}/values.yaml \
		--values={} \
		--set image.tag=${IMAGE_TAG}'

## Template chart with values. Useful for debugging.
helm-template: require-IMAGE_TAG require-ENVIRONMENT require-NAMESPACE
	@sed -i.bak "s/^appVersion:.*$$/appVersion: ${IMAGE_TAG}/" chart/Chart.yaml
	@sops exec-file chart/values/${ENVIRONMENT}/secrets.yaml 'helm --namespace=${NAMESPACE} --debug template ${OPTS} chart/  \
		--values=chart/values/${ENVIRONMENT}/values.yaml \
		--values={} \
		--set image.tag=${IMAGE_TAG}'

## Run Django tests (optionally pass APP)
test:
	@DJANGO_SETTINGS_MODULE=project.settings.test python manage.py test ${APP}

## Show help screen.
help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo
	@awk '/^[a-zA-Z\-0-9_]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "%-30s %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

