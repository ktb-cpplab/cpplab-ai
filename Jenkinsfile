pipeline {
    agent any

    environment {
        // 공통 환경 변수
        AWS_REGION = 'ap-northeast-2'
        ECR_CREDENTIALS_ID = 'ecr:ap-northeast-2:AWS_CREDENTIALS'
        GITHUB_CREDENTIALS_ID = 'github_token'
        ECS_CLUSTER_NAME = 'cpplab-ecs-cluster'
        ECS_SERVICE_NAME = 'my-ai-service'  // AI 서비스 이름
        BRANCH_NAME = "${env.GIT_BRANCH}"
        DOCKER_TAG = "${env.BUILD_NUMBER}"  // Jenkins build number
        AWS_CREDENTIALS_ID = 'AWS_CREDENTIALS'

        REPO = 'ktb-cpplab/cpplab-ai'
        // 팀원 A 관련 환경 변수
        DIR_A = 'recommend'
        ECR_REPO_A = '891612581533.dkr.ecr.ap-northeast-2.amazonaws.com/cpplab/recommend'

        // 팀원 B 관련 환경 변수
        DIR_B = 'simon'
        ECR_REPO_B = '891612581533.dkr.ecr.ap-northeast-2.amazonaws.com/cpplab/simon'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    currentBuild.description = 'Checkout'
                    // 저장소에서 코드 가져오기
                    git branch: 'main', url: "https://github.com/${REPO}.git", credentialsId: "${GITHUB_CREDENTIALS_ID}"
                }
            }
        }

        stage('Prepare Application Properties') {
            steps {
                withCredentials([file(credentialsId: 'application-properties', variable: 'PROPERTIES')]) {
                    sh "cp \$PROPERTIES recommend/application.properties"
                }
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build Image A') {
                    steps {
                        script {
                            currentBuild.description = 'Build Docker Image for Team A'
                            // 팀원 A의 Docker 이미지 빌드
                            dockerImageA = docker.build("${ECR_REPO_A}:${env.BUILD_NUMBER}", "${DIR_A}")
                        }
                    }
                }

                stage('Build Image B') {
                    steps {
                        script {
                            currentBuild.description = 'Build Docker Image for Team B'
                            // 팀원 B의 Docker 이미지 빌드
                            dockerImageB = docker.build("${ECR_REPO_B}:${env.BUILD_NUMBER}", "${DIR_B}")
                        }
                    }
                }
            }
        }

        stage('Push to ECR') {
            parallel {
                stage('Push Image A to ECR') {
                    steps {
                        script {
                            currentBuild.description = 'Push Docker Image Pickle to ECR'
                            docker.withRegistry("https://${ECR_REPO_A}", "${ECR_CREDENTIALS_ID}") {
                                dockerImageA.push("${env.BUILD_NUMBER}")
                                dockerImageA.push("latest")
                            }
                        }
                    }
                }

                stage('Push Image B to ECR') {
                    steps {
                        script {
                            currentBuild.description = 'Push Docker Image Simon to ECR'
                            docker.withRegistry("https://${ECR_REPO_B}", "${ECR_CREDENTIALS_ID}") {
                                dockerImageB.push("${env.BUILD_NUMBER}")
                                dockerImageB.push("latest")
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                script {
                    currentBuild.description = 'Deploy Multi-Container to ECS'
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_CREDENTIALS_ID}"]]) {
                        sh """
                        # ECS Task Definition을 업데이트하고, 다중 컨테이너로 배포 -> terraform으로 추가 작성해주어야하나?
                        aws ecs update-service --cluster ${ECS_CLUSTER_NAME} --service ${ECS_SERVICE_NAME} --force-new-deployment --region ${AWS_REGION}
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Build and Deploy Completed'
        }
        failure {
            echo 'Build or Deploy Failed'
        }
    }
}
