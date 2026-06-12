@echo off
echo ============================================
echo Building Spring Boot JAR file...
echo ============================================

cd backend\demo\demo
echo Running Maven build...
call mvn clean package -DskipTests
IF %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b 1
)

echo Build successful!
echo.

echo ============================================
echo Deploying JAR file...
echo ============================================

IF NOT EXIST "%DEPLOYMENT_TARGET%" mkdir "%DEPLOYMENT_TARGET%"
copy target\demo-0.0.1-SNAPSHOT.jar "%DEPLOYMENT_TARGET%\"
IF %ERRORLEVEL% NEQ 0 (
    echo Deployment failed!
    exit /b 1
)

echo.
echo ============================================
echo Deployment completed successfully!
echo ============================================