'''
Get all ECS Service info for an account and format the log data to stdout in json struct
'''

import boto3
import time
import os
from datetime import datetime
import json
import pytz
from dataclasses import dataclass, field

# set up boto client(s)

# set up region for boto3 clients 
region = 'us-east-1'
try:
    region = os.environ.get('AWS_REGION')
except Exception as e:
    print('could not find region via environment variable AWS_REGION, using default value: ', region)

# set up default client
ecs_client = boto3.client('ecs', region_name='us-east-1')
ec2_client = boto3.client('ec2', region_name='us-east-1')

if region != None:
    ecs_client = boto3.client('ecs', region_name=str(region))
    ec2_client = boto3.client('ec2', region_name=str(region))

#print('region used: ', region)

@dataclass
class ServiceData():
    serviceTag: str = ''
    serviceName: str = ''
    serviceArn: str = ''
    taskArns: list = field(default_factory=list)
    taskDefinitions: list = field(default_factory=list)
    cfStackName: str = ''
    containerType: str = '' # ec2 or fargate
    fargateMem: int = 0
    fargateVcpu: int = 0
    ec2InstanceType: str = ''
    desiredTasks: int = 0
    runningTasks: int = 0
    pendingTasks: int = 0
    desiredTaskMinutes: int = 0 # num of desired Tasks * 1
    runningTaskMinutes: int = 0 
    pendingTaskMinutes: int = 0
    desiredTaskSeconds: int = 0 # num of desired Tasks * 60 
    runningTaskSeconds: int = 0
    pendingTaskSeconds: int = 0
    desiredTaskMs: int = 0 # num of desired Tasks * 60 * 1000
    runningTaskMs: int = 0
    pendingTaskMs: int = 0    
    timeoutSecs: int = 0 #tsTimeoutSecs
    defaultWorkersPerModel: int = 0 #tsDefaultWorkersPerModel
    queueSize: int = 0 #tsQueueSize
    serviceCostPerMinute: float = 0.00

    def printData(self):
        print('==== SERVICE DATA ITEM ====')
        print('serviceTag: ', self.serviceTag)
        print('serviceName: ', self.serviceName)
        print('serviceArn: ', self.serviceArn)
        print('taskArns: ', self.taskArns)
        print('taskDefArns: ', self.taskDefinitions)
        print('cfStackName: ', self.cfStackName)
        print('containerType: ', self.containerType)
        print('fargateMem: ', self.fargateMem)
        print('fargateVcpu:', self.fargateVcpu)
        print('ec2InstanceType: ', self.ec2InstanceType)
        print('desiredTasks: ', self.desiredTasks)
        print('runningTasks: ', self.runningTasks)
        print('pendingTasks: ', self.pendingTasks)
        print('desiredTaskMin: ', self.desiredTaskMinutes)
        print('runningTaskMin: ', self.runningTaskMinutes)
        print('pendingTaskMin: ', self.pendingTaskMinutes)
        print('desiredTaskSec: ', self.desiredTaskSeconds)
        print('runningTaskSec: ', self.runningTaskSeconds)
        print('pendingTaskSec: ', self.pendingTaskSeconds)
        print('desiredTaskMs: ', self.desiredTaskMs)
        print('runningTaskMs: ', self.runningTaskMs)
        print('pendingTaskMs: ', self.pendingTaskMs)
        print('timeoutSecs: ', self.timeoutSecs)
        print('defaultWorkersPerModel: ', self.defaultWorkersPerModel)
        print('queueSize: ', self.queueSize)
        print('serviceCostPerMin: ', self.serviceCostPerMinute)
        print()

@dataclass
class ClusterData():
    clusterArn: str = ''
    serviceArnList: list = field(default_factory=list)
    serviceDataList: list = field(default_factory=list)

    def printData(self):
        print('clusterArn: ', self.clusterArn)
        print('# of services: ', len(self.serviceDataList))
        print('services: ', self.serviceArnList)
        for item in self.serviceDataList:
            print(item.printData())
        

def ConvertListToJsonLogFormat(inputList):
    
    for cluster in inputList:
        clusterArn = cluster.clusterArn
        sep = '/'
        head, sep, tail = clusterArn.partition('/')
        clusterName = tail

        if cluster.serviceDataList != []:
            
            for service in cluster.serviceDataList:
                logTime = time.time()

                jsonData = {}

                jsonData['serviceTag'] = service.serviceTag
                jsonData['clusterName'] = clusterName
                jsonData['cloudFormationStackName'] = service.cfStackName
                jsonData['containerType'] = service.containerType
                if service.containerType == 'FARGATE':
                   jsonData['FarGateMemory'] = service.fargateMem
                   jsonData['FarGatevCPU'] = service.fargateVcpu
                if service.containerType == 'EC2':
                    jsonData['EC2InstanceType'] = service.ec2InstanceType
                jsonData['desiredTasks'] = service.desiredTasks
                jsonData['runningTasks'] = service.runningTasks
                jsonData['pendingTasks'] = service.pendingTasks
                jsonData['desiredTaskMinutes'] = service.desiredTaskMinutes
                jsonData['runningTaskMinutes'] = service.runningTaskMinutes
                jsonData['pendingTaskMinutes'] = service.pendingTaskMinutes
                jsonData['desiredTaskSeconds'] = service.desiredTaskSeconds
                jsonData['runningTaskSeconds'] = service.runningTaskSeconds
                jsonData['pendingTaskSeconds'] = service.pendingTaskSeconds
                jsonData['desiredTaskMS'] = service.desiredTaskMs
                jsonData['runningTaskMS'] = service.runningTaskMs
                jsonData['pendingTaskMS'] = service.pendingTaskMs
                if service.timeoutSecs != 0:
                    jsonData['timeoutSecs'] = service.timeoutSecs
                if service.defaultWorkersPerModel != 0:
                    jsonData['defaultWorkersPerModel'] = service.defaultWorkersPerModel
                if service.queueSize != 0:
                    jsonData['queueSize'] = service.queueSize
                jsonData['serviceCostPerMinute'] = service.serviceCostPerMinute
                dateTime = datetime.now(pytz.UTC)
                formattedTime = dateTime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                jsonData['dateTime1'] = formattedTime

                # only log data with valid service tags
                if service.serviceTag != '':
                    print(json.dumps(jsonData, default=str))
                #    print()
                #else:
                #    print('=================================') 
                #    print('serviceTag empty, item dropped! ')
                #    print('clusterName: ', clusterName)
                #    print('=================================')

def GetClusterList():

    resp = {}
    try:
        resp = ecs_client.list_clusters()
        
    except Exception as e:
        print('error during client call: ', e)

    clusterList = resp['clusterArns']

    return clusterList

def GetServiceList(clusterList):

    dataItemList = []

    for item in clusterList:
        
        dataItem = ClusterData()
        resp = {}
        
        try:
            resp = ecs_client.list_services(
                cluster=item,
                maxResults=100
            )
        
        except Exception as e:
            print('error during client call: ', e)

        dataItem.clusterArn = item
        dataItem.serviceArnList = resp['serviceArns']

        dataItemList.append(dataItem)

    return dataItemList

def GetServiceInfo(clusterArn, serviceList):
    nullServiceInputCount = 0
    resp = {}

    try: 
        resp = ecs_client.describe_services(
            cluster=clusterArn,
            services=serviceList,
            include=['TAGS']
        )

        # clean data
        for item in resp['services']:
            del item['events']

    except Exception as e:
        nullServiceInputCount+=1

    if serviceList != 0 and resp != {}:
        return resp['services']
    else:
        return []

# return a list of lists where the composing list sizes are 10 max
def SplitServicesIntoListofTen(inputList):
    outputList = []
    listOfTen = []

    count = 1
    for item in inputList:

        listOfTen.append(item)
        if count % 10 == 0:
            outputList.append(listOfTen)
            listOfTen=[]
        count+=1
        if item == inputList[-1]:
            outputList.append(listOfTen)

    return outputList

def CollectServiceData(inputList):

    itemCount = 0
    errorCount = 0
    
    for item in inputList:
        itemCount+=1

        servicesResp = []
        serviceDataList = []
        stackName = ''

        if item.serviceArnList != [] and len(item.serviceArnList) <= 10:
            servicesResp = GetServiceInfo(item.clusterArn, item.serviceArnList)
            stackName = GetStackNameFromClusterId(item.clusterArn)            

        else: # service list is greater than 10 
            listOfTenServicesList =  SplitServicesIntoListofTen(item.serviceArnList)
            stackName = GetStackNameFromClusterId(item.clusterArn)
            respTotal = []
            for i in listOfTenServicesList:
                respPart = GetServiceInfo(item.clusterArn, i)
                respTotal+=respPart
            
            servicesResp = respTotal

        for entry in servicesResp:

            serviceData = ServiceData()
            serviceTag = ''
            ec2InstanceType = ''
            # safe guard tag check
            try:
                
                if entry['tags']:
                    for index in entry['tags']:
                        if index['key'] == 'Service':
                            serviceTag = index['value']

            except Exception as e:
                errorCount+=1
                            
            serviceData.serviceTag = serviceTag
            serviceData.serviceName = str(entry['serviceName'])
            serviceData.serviceArn = str(entry['serviceArn'])
            serviceData.cfStackName = stackName
            serviceData.containerType = str(entry['launchType'])
            if str(entry['launchType']) == 'EC2':
                ec2InstanceType = GetEc2InstanceTypeFromClusterId(item.clusterArn)
            serviceData.ec2InstanceType = ec2InstanceType
            serviceData.desiredTasks = int(entry['desiredCount'])
            serviceData.runningTasks = int(entry['runningCount'])
            serviceData.pendingTasks = int(entry['pendingCount'])
            serviceData.desiredTaskMinutes = int(entry['desiredCount']) * 1
            serviceData.runningTaskMinutes = int(entry['runningCount']) * 1
            serviceData.pendingTaskMinutes = int(entry['pendingCount']) * 1
            serviceData.desiredTaskSeconds = int(entry['desiredCount']) * 60
            serviceData.runningTaskSeconds = int(entry['runningCount']) * 60
            serviceData.pendingTaskSeconds = int(entry['pendingCount']) * 60
            serviceData.desiredTaskMs = (int(entry['desiredCount']) * 60) * 1000
            serviceData.runningTaskMs = (int(entry['runningCount']) * 60) * 1000
            serviceData.pendingTaskMs = (int(entry['pendingCount']) * 60) * 1000
            serviceData.serviceCostPerMinute = float(0.00)
            
            serviceDataList.append(serviceData)

        item.serviceDataList = serviceDataList                    

    return inputList            

def GetTaskArns(clusterDataList):

    for cluster in clusterDataList:
        serviceDataList = []
        clusterArn = cluster.clusterArn

        if cluster.serviceDataList != []:
            
            for service in cluster.serviceDataList:
                resp = {}

                try:
                    resp = ecs_client.list_tasks(
                        cluster=clusterArn,
                        serviceName=service.serviceName,
                        launchType=service.containerType,
                        maxResults=100 # FUTURE: this might be a problem for summarization scaling in the future 
                    )
                    
                    taskArnList = resp['taskArns']
                    #print(taskArnList)
                    service.taskArns = taskArnList
                    
                except Exception as e:
                    print('error during client call: ', e)

                serviceDataList.append(service)
        
        cluster.serviceDataList = serviceDataList

    return clusterDataList                    

def GetFargateInfo(clusterDataList):
    
    for cluster in clusterDataList:
        serviceDataList = []
        clusterArn = cluster.clusterArn

        if cluster.serviceDataList != []:
            
            for service in cluster.serviceDataList:
    
               if service.taskArns != []:
                    resp = {}
                    
                    try:
                        resp = ecs_client.describe_tasks(
                            cluster=clusterArn,
                            tasks=service.taskArns,
                            include=['TAGS']
                        )

                        taskDefs = []
                        # grab fargate and taskDef data
                        if service.containerType != 'EC2':
                            
                            mem = 0
                            cpu = 0
                            for task in resp['tasks']:
                                mem += int(task['memory'])
                                cpu += int(task['cpu'])
                                taskDefs.append(task['taskDefinitionArn'])

                            service.fargateMem =  mem
                            service.fargateVcpu = cpu
                            service.taskDefinitions = taskDefs

                        # just grab taskDef data
                        else:
                            for task in resp['tasks']:
                                taskDefs.append(task['taskDefinitionArn'])
                            
                            service.taskDefinitions = taskDefs

                    except Exception as e:
                        print('error during client call: ', e)

               serviceDataList.append(service)
  
        cluster.serviceDataList = serviceDataList
    
    return clusterDataList

def GetStackNameFromClusterId(clusterArn):

    stackName = ''

    resp = {}
    try:
        resp = ecs_client.describe_clusters(
            clusters=[clusterArn],
            include=['ATTACHMENTS','CONFIGURATIONS','SETTINGS','STATISTICS','TAGS']
        )

    except Exception as e:
        print('error during client call: ', e)

    tags = resp['clusters'][0]['tags']

    for item in tags:
        if item['key'] == 'aws:cloudformation:stack-name':
            stackName = item['value']

    return stackName

def GetEc2InstanceTypeFromClusterId(clusterArn):

    ec2InstanceType = ''

    # list container instances for each cluster
    # describe the container instances for each cluster
    # get the underlying EC2 instance type from the container desc 
    # double check that the first one grabbed is good (they should all match in the cluster)
    resp = {}
    try:
        resp = ecs_client.list_container_instances(
            cluster=clusterArn,
        )

    except Exception as e:
        print('error during client call: ', e)

    containerList = resp['containerInstanceArns']

    if containerList != []:

        resp2 = {}
        try:
            resp2 = ecs_client.describe_container_instances(
                cluster=clusterArn,
                containerInstances=containerList
            )
        except Exception as e:
            print('error during client call: ', e)

        instanceIdList = []

        for item in resp2['containerInstances']:
            instanceIdList.append(item['ec2InstanceId'])

        resp3 = {}
        try:
            resp3 = ec2_client.describe_instances(
                InstanceIds=instanceIdList
            )
        except Exception as e:
            print('error during client call: ', e)

        instanceTypeList = []

        reservations = resp3['Reservations']
        for r in reservations:
            for instances in r['Instances']:
                instanceTypeList.append(instances['InstanceType'])

        # check if all items in the list are identical
        #identical = instanceTypeList[1:] == instanceTypeList[:-1]
        #print('truth: ', identical, ' value: ', instanceTypeList)

        ec2InstanceType = instanceTypeList[0]
    
    return ec2InstanceType


def GetTaskDetails(clusterDataList):
    
    for cluster in clusterDataList:
        serviceDataList = []
        clusterArn = cluster.clusterArn

        if cluster.serviceDataList != []:
            
            for service in cluster.serviceDataList:
    
               # only GPU services are using torch serv ?!?!?!
               #service.containerType != 'FARGATE' and 
               if service.taskDefinitions != []:
                    resp = {}
                    
                    try:
                        resp = ecs_client.describe_task_definition(
                            taskDefinition=str(service.taskDefinitions[0]), # all tasks have the same config, grab the first and move on
                            include=['TAGS']
                        )
                        defaultWorkersKey = 'TS_DEFAULT_WORKERS_PER_MODEL'
                        requestTimeoutKey = 'MT_REQUEST_TIMEOUT'
                        queueSizeKey = 'TS_JOB_QUEUE_SIZE'
                        tsTimeoutSecs = 0
                        tsDefaultWorkersPerModel = 0
                        tsQueueSize = 0
                        
                        taskDef = resp['taskDefinition']
                        for item in taskDef['containerDefinitions']:
                            env = item['environment']
                            for var in item['environment']:
                                if var['name'] == defaultWorkersKey:
                                    tsDefaultWorkersPerModel = var['value']
                                    #print(var['name'], var['value'])
                                if var['name'] == requestTimeoutKey:
                                    tsTimeoutSecs = var['value']
                                    #print(var['name'], var['value'])
                                if var['name'] == queueSizeKey:
                                    tsQueueSize = var['value']
                                    #print(var['name'], var['value'])
                                    
                        service.timeoutSecs = int(tsTimeoutSecs)
                        service.defaultWorkersPerModel = int(tsDefaultWorkersPerModel)
                        service.queueSize = int(tsQueueSize)
                        
                    except Exception as e:
                        print('error during client call: ', e)  

               serviceDataList.append(service)
  
        cluster.serviceDataList = serviceDataList
    
    return clusterDataList

def logToScreen(inputList):

    for item in inputList:
        item.printData()


def CollectServiceMetrics():

    clusterList = GetClusterList()
    clusterDataList = GetServiceList(clusterList)  
    clusterAndServiceDataList = CollectServiceData(clusterDataList)
    cstDataList = GetTaskArns(clusterAndServiceDataList)
    cstUpdatedDataList = GetFargateInfo(cstDataList)
    cstUpdatedDataList = GetTaskDetails(cstUpdatedDataList)
    ConvertListToJsonLogFormat(cstUpdatedDataList)

if __name__ == "__main__":

    startTime = time.monotonic()
    PROC_INTERVAL = 60.0
    DEBUG = 0
    cycles = 0
    driftSumSeconds = 0
    runtimeSumSeconds = 0

    while(True):

        cycles+=1
        start = time.time()

        CollectServiceMetrics()

        end = time.time()
        elapsedTime = end - start
        runtimeSumSeconds += elapsedTime
        avgRuntime = runtimeSumSeconds / cycles
       
        if DEBUG:
            print()
            print('elapsed: ', end - start)
            print('avg runtime: ', avgRuntime)
            drift = abs(avgRuntime - elapsedTime)
            driftSumSeconds+=drift
            print('drift: ', drift * 1000, 'ms')
            print('avg drift: ', (driftSumSeconds / cycles) * 1000, 'ms')
            print()

        time.sleep(PROC_INTERVAL - ((time.monotonic() - startTime) % PROC_INTERVAL))
