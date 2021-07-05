pipeline {
    agent any
    parameters { 
        string(defaultValue: '', name: 'ENV_TAG', description: '请根据发布类型进行选择发布：\n1，输入-UAT-发布到测试环境\n2，输入-DEV-发布到开发' )
        string(defaultValue: '', name: 'CONFIG_SERVER_URL', description: 'apollo 配置参数config_server_url\n2，例如: http://192.168.1.71:8080')
        string(defaultValue: '', name: 'APP_ID', description: 'apollo 配置参数app_id\n2，例如: webterminal')
        string(defaultValue: '', name: 'NAMESPACE', description: 'apollo 配置参数namespace\n2，例如: application')
        string(defaultValue: '', name: 'CLUSTER_NAME', description: 'apollo 配置参数cluster_name\n2，例如: default')
    }
    environment {
        tag_image = new Date().format("yyyyMMddHHmm")
        repositoryname = 'somp'
        imagename = 'somp-webterminal'
        containername = 'somp-webterminal'
        port = '443'
        projectfs = '/app/webterminal'
        imageport = '443'
        clientserver_uat = '192.168.103.240'
        clientserver_dev = '192.168.1.82'

        dockerRun1 = "docker rm ${containername} -f || true"
        dockerRun3 = "docker login registry.bwda.net -u somp -p Somp123456"
        dockerRun4 = "docker image pull registry.bwda.net/${repositoryname}/${imagename}:${tag_image}"
        docker_name = "--privileged=true registry.bwda.net/${repositoryname}/${imagename}:${tag_image}"
        dockerRun_uat = "docker run --name ${containername} -d -p ${port}:443  "
        dockerRun_dev = "docker run --name ${containername} -d -p ${port}:443  "

    }
    
    stages {
        

        stage("构建镜像") {
            steps {
                script {
                    stage('Build image') {
                        app = docker.build("registry.bwda.net/${repositoryname}/${imagename}:${tag_image}")
                        docker.withRegistry('http://registry.bwda.net', 'registry-harbor-223') {
                            app.push("${tag_image}")
                        }   
                    }       
                }
            }
        }

        stage('环境发布') {
            steps {
            echo "code sync"
                script {
                    if (env.ENV_TAG == 'UAT') {
                        echo '发布到测试环境'
                            sshagent(['192.168.103.240-ssh-docker']){
                            sh "ssh -o StrictHostKeyChecking=no root@${clientserver_uat} ${dockerRun1}"
                            sh "ssh -o StrictHostKeyChecking=no root@${clientserver_uat} ${dockerRun3}"
                            sh "ssh -o StrictHostKeyChecking=no root@${clientserver_uat} ${dockerRun4}"
                            //
                            if (env.CONFIG_SERVER_URL != "null" and env.APP_ID != "null" and env.NAMESPACE != "null" and env.CLUSTER_NAME != "null"){
                                sh "ssh -o StrictHostKeyChecking=no root@${clientserver_uat} ${dockerRun_uat} -e config_server_url=${env.CONFIG_SERVER_URL} -e app_id=${env.APP_ID} -e namespace=${env.NAMESPACE} -e cluster_name=${env.CLUSTER_NAME} ${docker_name}"
                            }
                            else{
                                sh "ssh -o StrictHostKeyChecking=no root@${clientserver_uat} ${dockerRun_uat} ${docker_name}"
                            }

                        }
                    }
                    
                    else {
                        if (env.ENV_TAG == 'DEV') {
                            echo '发布到开发环境'
                            
                            sshagent(['192.168.1.82-ssh-docker']){
                                sh "ssh -o StrictHostKeyChecking=no root@${clientserver_dev} ${dockerRun1}"
                                sh "ssh -o StrictHostKeyChecking=no root@${clientserver_dev} ${dockerRun3}"
                                sh "ssh -o StrictHostKeyChecking=no root@${clientserver_dev} ${dockerRun4}"
                                if (env.CONFIG_SERVER_URL != "null" and env.APP_ID != "null" and env.NAMESPACE != "null" and env.CLUSTER_NAME != "null"){
                                    sh "ssh -o StrictHostKeyChecking=no root@${clientserver_dev} ${dockerRun_dev} -e config_server_url=${env.CONFIG_SERVER_URL} -e app_id=${env.APP_ID} -e namespace=${env.NAMESPACE} -e cluster_name=${env.CLUSTER_NAME} ${docker_name}"
                                }
                                else{
                                    sh "ssh -o StrictHostKeyChecking=no root@${clientserver_dev} ${dockerRun_dev} ${docker_name}"
                                }

                            } 
                        }
                    }
                }
            }
        }
    
        stage("写入InfluxDB") {
            steps {
                script {
                    if (currentBuild.currentResult == 'UNSTABLE') {
                        currentBuild.result = "UNSTABLE"
                    } else {
                        currentBuild.result = "SUCCESS"
                    }
                    step([$class: 'InfluxDbPublisher', customData: null, customDataMap: null, customPrefix: null, jenkinsEnvParameterField: 'build_agent_name=' + 'master' + '\n' + 'build_status_message=' + currentBuild.description, target: 'influxdb'])    
                }
            }
        }
    }
}
