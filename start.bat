@echo off
echo ========================================
echo FP-Growth Recommender System
echo ========================================
echo.

:menu
echo Choisissez une option:
echo.
echo 1. Demarrer l'application
echo 2. Arreter l'application
echo 3. Reinitialiser (supprimer les donnees)
echo 4. Voir les logs
echo 5. Quitter
echo.
set /p choice="Votre choix (1-5): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto reset
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto end
goto menu

:start
echo.
echo Demarrage de l'application...
echo.
docker-compose up --build
goto menu

:stop
echo.
echo Arret de l'application...
echo.
docker-compose down
echo.
echo Application arretee!
echo.
pause
goto menu

:reset
echo.
echo ATTENTION: Cette action va supprimer toutes les donnees!
set /p confirm="Etes-vous sur? (O/N): "
if /i "%confirm%"=="O" (
    echo.
    echo Reinitialisation en cours...
    docker-compose down -v
    echo.
    echo Reinitialisation terminee!
    echo.
) else (
    echo.
    echo Operation annulee.
    echo.
)
pause
goto menu

:logs
echo.
echo Affichage des logs...
echo.
docker-compose logs --tail=50
echo.
pause
goto menu

:end
echo.
echo Au revoir!
exit
