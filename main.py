from cdk8s import App
from charts.nginx import NginxChart

app = App()
NginxChart(app)
app.synth()

