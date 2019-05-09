#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel-app', color: 'danger'

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
            sh "api/deploy/test/the_test.sh &&" +
               "importer/deploy/test/test.sh &&" +
               "analyzer/deploy/test/test.sh"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            def importer = docker.build("build.app.amsterdam.nl:5000/stadswerken/citydynamics_importer:${env.BUILD_NUMBER}", "importer")
                importer.push()
                importer.push("acceptance")

            def analyzer = docker.build("build.app.amsterdam.nl:5000/stadswerken/citydynamics_analyzer:${env.BUILD_NUMBER}", "analyzer")
                analyzer.push()
                analyzer.push("acceptance")

            def api = docker.build("build.app.amsterdam.nl:5000/stadswerken/citydynamics:${env.BUILD_NUMBER}", ".")
                api.push()
                api.push("acceptance")
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                def image = docker.image("build.app.amsterdam.nl:5000/stadswerken/citydynamics:${env.BUILD_NUMBER}")
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
        slackSend channel: '#stadinbalans', color: 'warning', message: 'City dynamics is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                def api = docker.image("build.app.amsterdam.nl:5000/stadswerken/citydynamics:${env.BUILD_NUMBER}")
                def analyzer = docker.image("build.app.amsterdam.nl:5000/stadswerken/citydynamics_analyzer:${env.BUILD_NUMBER}")
                def importer = docker.image("build.app.amsterdam.nl:5000/stadswerken/citydynamics_importer:${env.BUILD_NUMBER}")

                analyzer.push("production")
                analyzer.push("latest")

                importer.push("production")
                importer.push("latest")

                api.push("production")
                api.push("latest")
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
