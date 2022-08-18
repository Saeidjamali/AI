SHELL := /bin/bash

export AWS_PROFILE ?= intellithing

.PHONY: publish-artifacts-stage
publish-artifacts-stage: ENV=stage
publish-artifacts-stage: --publish-artifacts

.PHONY: deploy-stage
deploy-stage: ENV=stage
deploy-stage: --deploy


--publish-artifacts:
	@echo "--- :shipit: Publishing artifacts to '$(ENV)' environment :shipit:"
	
	tar -czf /tmp/chatbot.tgz --exclude models_archive * ../requirements.txt && \
	aws s3  cp  /tmp/chatbot.tgz s3://ithing-$(ENV)-artifacts/archives/
	
--deploy:
	@echo "--- :shipit: Deploying to '$(ENV)' environment :shipit:"
	
	aws autoscaling start-instance-refresh \
		--auto-scaling-group-name "ithing-$(ENV)-chatbot-asg" \
		--preferences MinHealthyPercentage=50,InstanceWarmup=100
