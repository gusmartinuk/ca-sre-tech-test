import cdk8s_plus_26 as kplus
import cdk8s
import os

app = cdk8s.App()                       # Initialize a cdk8s app. This represents your CDK8s application.
chart = cdk8s.Chart(app, "tech-test")   # Create a chart. Charts are the basic deployment units in CDK8s, similar to Kubernetes manifests. 
                                        # docs: https://cdk8s.io/docs/latest/basics/chart/
# Lines 8-11: Create a dictionary containing the contents of files in the './public' directory.
site_contents_dict = {                  # This dictionary is then used to create a Kubernetes ConfigMap.
    filename: open(os.path.join("./public", filename)).read()   # os.path.join("./public", filename) creates the full file path for each file and open().read() reads file 
    for filename in os.listdir("./public")                      # os.listdir("./public") lists all filenames in the ./public directory.
}

# Create a ConfigMap from the files in the 'public' directory. ConfigMaps are used to store non-confidential data in key-value pairs.
config_map = kplus.ConfigMap(           # docs: https://cdk8s.io/docs/latest/plus/cdk8s-plus-26/config-map/ 
    chart,
    "configmap",
    data=site_contents_dict,
    metadata=cdk8s.ApiObjectMetadata(name="tech-test-configmap"),
)

# Create a Volume from the ConfigMap. Volumes in Kubernetes are used to store data and make it accessible to containers.
volume = kplus.Volume.from_config_map(chart, "volume", config_map=config_map) # docs: https://cdk8s.io/docs/latest/plus/cdk8s-plus-25/pod/#adding-volumes

# Define a Deployment. Deployments manage stateless applications on Kubernetes, ensuring specified number of pod replicas run.
deployment = kplus.Deployment(      # docs: https://cdk8s.io/docs/latest/basics/api-object/#resource-names
    chart,
    "deployment",
    metadata=cdk8s.ApiObjectMetadata(
        name="tech-test-deployment",
    ),    
    replicas=5  # Set the number of replicas to 5  Additional Task 2 
)

# Add an Nginx container to the deployment with specific configurations.
deployment.add_container(   # docs: https://cdk8s.io/docs/latest/reference/cdk8s-plus-25/python/#add_container
    image="nginx:latest",   # Specify the Docker image to use.
    port=80,                # Expose port 80 of the container.
    name="nginx",           # Name of the container.
    security_context=kplus.ContainerSecurityContextProps(
        ensure_non_root=False, 
        read_only_root_filesystem=False  # Set root filesystem to writable. (It was True before and updated)
    ),
    volume_mounts=[             # Mount the previously created volume to the container.
        kplus.VolumeMount(  # docs: https://cdk8s.io/docs/latest/reference/cdk8s-plus-26/python/#volumemount
            path="/usr/share/nginx/html",
            volume=volume,
        )
    ],
)

# Create a Service to expose the deployment. Services provide a way to access applications running on a set of Pods.
service = kplus.Service(    # docs: https://cdk8s.io/docs/latest/plus/cdk8s-plus-26/service/
    chart,
    "service",
    ports=[kplus.ServicePort(port=80, target_port=8080)],   # Map port 80 of the service to port 8080 of the container.
    type=kplus.ServiceType.NODE_PORT,                       # Expose the service outside the cluster using a node port.
    selector=deployment,                                    # Select the deployment that this service should route to.
    metadata=cdk8s.ApiObjectMetadata(name="tech-test-service"),
)

if __name__ == "__main__":
    app.synth()  # Synthesize the CDK8s app into Kubernetes manifests.
