pipeline {
    agent any

    environment {
        // 공통 환경 변수
        AWS_REGION = 'ap-northeast-2'
        ECR_CREDENTIALS_ID = 'ecr:ap-northeast-2:AWS_CREDENTIALS'
        GITHUB_CREDENTIALS_ID = 'github_token'
        ECS_CLUSTER_NAME = 'cpplab-ecs-cluster'
        ECS_SERVICE_NAME = 'my-ai-service'
        AWS_CREDENTIALS_ID = 'AWS_CREDENTIALS'

        REPO = 'ktb-cpplab/cpplab-ai'
        ECR_REPO = '891612581533.dkr.ecr.ap-northeast-2.amazonaws.com/cpplab/ai'

        // 팀원별 디렉토리 설정
        DIR_A = 'recommend'
        DIR_B = 'project'

        // 디렉토리별 빌드 넘버 관리
        BUILD_NUMBER_A = "${env.BUILD_NUMBER}-peter"  // Team A의 빌드 넘버
        BUILD_NUMBER_B = "${env.BUILD_NUMBER}-simon"  // Team B의 빌드 넘버

        //피클 모델 파일 정보
        S3_BUCKET = 'cpplab-pickle'
        S3_MODEL_PATH = 'models/'  // S3 상의 모델 파일 경로
        LOCAL_MODEL_DIR = 'recommend'  // 로컬에서 파일을 저장할 경로
    }

    stages {
        stage('Cleanup Docker Cache') {
            steps {
                script {
                    currentBuild.description = 'Cleanup Docker Cache'
                    sh """
                    docker system prune -af --volumes
                    """
                }
            }
        }
        
        stage('Checkout') {
            steps {
                script {
                    currentBuild.description = 'Checkout'
                    // 저장소에서 코드 가져오기
                    git branch: env.BRANCH_NAME, url: "https://github.com/${REPO}.git", credentialsId: "${GITHUB_CREDENTIALS_ID}"
                }
            }
        }

        stage('Download Model from S3') {
            steps {
                script {
                    currentBuild.description = 'Download Model from S3'
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_CREDENTIALS_ID}"]]) {
                        sh """
                        # recommend/models 폴더 생성
                        mkdir -p recommend/models
                        mkdir -p recommend/mecab/mecab-ko-dic-2.1.1-20180720
                        
                        # S3에서 모델 파일 다운로드
                        aws s3 cp s3://cpplab-pickle/models/ recommend/models/ --recursive
                        # S3에서 모델2 파일 다운로드
                        aws s3 cp s3://cpplab-mecab/mecab-0.996-ko-0.9.2/ recommend/mecab/mecab-ko-dic-2.1.1-20180720/ --recursive
                        """
                    }
                }
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build Image A') {
                    steps {
                        script {
                            currentBuild.description = 'Build Docker Image for Team A'
                            // Team A의 Docker 이미지 빌드
                            dockerImageA = docker.build("${ECR_REPO}:${DIR_A}-${BUILD_NUMBER_A}", "${DIR_A}")
                        }
                    }
                }

                stage('Build Image B') {
                    steps {
                        script {
                            currentBuild.description = 'Build Docker Image for Team B'
                            // Team B의 Docker 이미지 빌드
                            dockerImageB = docker.build("${ECR_REPO}:${DIR_B}-${BUILD_NUMBER_B}", "${DIR_B}")
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
                            currentBuild.description = 'Push Docker Image A to ECR'
                            docker.withRegistry("https://${ECR_REPO}", "${ECR_CREDENTIALS_ID}") {
                                dockerImageA.push("${DIR_A}-${BUILD_NUMBER_A}")
                                dockerImageA.push("${DIR_A}-latest")
                            }
                        }
                    }
                }

                stage('Push Image B to ECR') {
                    steps {
                        script {
                            currentBuild.description = 'Push Docker Image B to ECR'
                            docker.withRegistry("https://${ECR_REPO}", "${ECR_CREDENTIALS_ID}") {
                                dockerImageB.push("${DIR_B}-${BUILD_NUMBER_B}")
                                dockerImageB.push("${DIR_B}-latest")
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
                        # ECS 서비스 업데이트를 통해 새 배포 강제
                        aws ecs update-service --cluster ${ECS_CLUSTER_NAME} --service ${ECS_SERVICE_NAME} --force-new-deployment --region ${AWS_REGION}
                        """
                    }
                }
            }
        }
    }

    post {
        success {
        withCredentials([string(credentialsId: 'Discord-AI-Webhook', variable: 'DISCORD')]) {
            discordSend description: """
            제목 : ${currentBuild.displayName}
            결과 : ${currentBuild.result}
            실행 시간 : ${currentBuild.duration / 1000}s
            """,
            link: env.BUILD_URL, result: currentBuild.currentResult,
            title: "${env.JOB_NAME} : ${currentBuild.displayName} 성공",
            webhookURL: "$DISCORD"
        }
    }
        failure {
            withCredentials([string(credentialsId: 'Discord-AI-Webhook', variable: 'DISCORD')]) {
                        discordSend description: """
                        제목 : ${currentBuild.displayName}
                        결과 : ${currentBuild.result}
                        실행 시간 : ${currentBuild.duration / 1000}s
                        """,
                        link: env.BUILD_URL, result: currentBuild.currentResult,
                        title: "${env.JOB_NAME} : ${currentBuild.displayName} 실패",
                        webhookURL: "$DISCORD"
            }
        }
        always {
            echo 'Build and Deploy Completed'
            sh 'rm -rf recommend/models'
            sh 'rm -rf recommend/mecab'
        }
    }
}
