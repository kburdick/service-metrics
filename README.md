Python script that collects the ECS container / task information within an AWS account and logs the data as a structured json doc to stdout.
- Provides a log of information not available within the ECS console
- Connect log output to a queryable backend log ingest to make graphs and get an understanding of your services behaviors using the metrics
- graph the metrics from your databse in something like grafana for quick visual insights to stack health and if tasks are operating within their limits

Future:
- collect and format additional metrics
- handle more complex task definition / service information 
- add extensible support for different log formats
