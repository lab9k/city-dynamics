#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage("Checkout") {
        checkout scm
    }

    stage('Test') {
        tryStep "test", {
            sh "docker-compose -p testcitydynamics -f web/deploy/test/docker-compose.yml build && " +
	       "docker-compose -p testcitydynamics -f web/deploy/test/docker-compose.yml down && " +
               "docker-compose -p testcitydynamics -f web/deploy/test/docker-compose.yml up tests"
        }, {
            sh "docker-compose -p testcitydynamics -f web/deploy/test/docker-compose.yml down"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            def importer = docker.build("build.datapunt.amsterdam.nl:5000/stadswerken/city_dynamics_importer:${env.BUILD_NUMBER}", "importer")
            importer.push()
            importer.push("acceptance")

            def analyzer = docker.build("build.datapunt.amsterdam.nl:5000/stadswerken/city_dynamics_analyzer:${env.BUILD_NUMBER}", "analyzer")
                analyzer.push()
                analyzer.push("acceptance")

            def web = docker.build("build.datapunt.amsterdam.nl:5000/stadswerken/city_dynamics:${env.BUILD_NUMBER}", "web")
            web.push()
            web.push("acceptance")
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                def image = docker.image("build.datapunt.amsterdam.nl:5000/stadswerken/city_dynamics:${env.BUILD_NUMBER}")
                image.pull()
                image.push("acceptance")
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-citydynamics.yml'],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'City dynamics is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                def kibana = docker.image("build.datapunt.amsterdam.nl:5000/stadswerken/city_dynamics:${env.BUILD_NUMBER}")
                kibana.pull()
                kibana.push("production")
                kibana.push("latest")
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-citydynamics.yml'],
                ]
            }
        }
    }
}
