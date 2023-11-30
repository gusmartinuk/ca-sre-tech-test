import cdk8s_plus_26 as kplus
import cdk8s
from cdk8s import Chart, Duration

import os

class NginxChart(Chart):
    def __init__(self, app, id='tech-test', **kwargs):
        super().__init__(app, id, **kwargs)
        
        # Create ConfigMap, Deployment, and Service
        self.create_config_map()
        self.create_deployment()
        self.create_service()

    def create_config_map(self):
        # Code to create ConfigMap
        site_contents_dict = {
            filename: open(os.path.join("./public", filename)).read()
            for filename in os.listdir("./public")
        }
        self.config_map = kplus.ConfigMap(
            self,
            "configmap",
            data=site_contents_dict,
            metadata=cdk8s.ApiObjectMetadata(name="tech-test-configmap"),
        )

    def create_deployment(self):
        # Define a Deployment. Deployments manage stateless applications on Kubernetes, ensuring specified number of pod replicas run.
        volume = kplus.Volume.from_config_map(self, "volume", config_map=self.config_map)
        self.deployment = kplus.Deployment(       # docs: https://cdk8s.io/docs/latest/basics/api-object/#resource-names
            self,
            "deployment",
            metadata=cdk8s.ApiObjectMetadata(
                    name="tech-test-deployment", 
                    labels={"app": "nginx"}  
                ),
            replicas=5  # Set the number of replicas to 5  Additional Task 2 
        )
        
        # Add an Nginx container to the deployment with specific configurations.
        self.deployment.add_container(       # docs: https://cdk8s.io/docs/latest/reference/cdk8s-plus-26/python/#add_container
            image="nginx:latest",       # Specify the Docker image to use.
            port=80,                    # Expose port 80 of the container.
            name="nginx",               # Name of the container.
            security_context=kplus.ContainerSecurityContextProps(
                ensure_non_root=False, 
                read_only_root_filesystem=False  # Set root filesystem to writable. (It was True before and updated)
            ),
            volume_mounts=[           # Mount the previously created volume to the container.
                kplus.VolumeMount(    # docs: https://cdk8s.io/docs/latest/reference/cdk8s-plus-26/python/#volumemount  
                    path="/usr/share/nginx/html",
                    volume=volume,
                )
            ],
            liveness=kplus.Probe.from_http_get(     # https://cdk8s.io/docs/latest/reference/cdk8s-plus-26/python/#probe
                path="/",
                port=80,
                initial_delay_seconds=Duration.seconds(30),
                period_seconds=Duration.seconds(10),
                timeout_seconds=Duration.seconds(5)
            )
        )

    # Create a Service to expose the deployment. Services provide a way to access applications running on a set of Pods.
    def create_service(self):
        # Create the Service
        service = kplus.Service(
            self,
            "service",
            ports=[kplus.ServicePort(port=80, target_port=8080)],   # Map port 80 of the service to port 8080 of the container.
            type=kplus.ServiceType.NODE_PORT,                       # Expose the service outside the cluster using a node port.
            selector=self.deployment,                               # Select the deployment that this service should route to.
            metadata=cdk8s.ApiObjectMetadata(name="tech-test-service"),
        )
