@echo off
echo   ---------------------------------------------------------------------------
echo   ^| Vista/Win7 用户请注意：                                                 ^|
echo   ^| 为保证安装正确，在执行本文件时，请"右键"选择本文件-^>"以管理员身份运行"  ^|
echo   ---------------------------------------------------------------------------
pause
if not exist %SystemRoot%\System32\drivers\etc\hosts goto not_necessary
echo;
echo 正在删除已有文件.....
del %SystemRoot%\System32\drivers\etc\hosts
if not exist %SystemRoot%\System32\drivers\etc\hosts goto success
echo ^^^操作失败，请确认您是以管理员身份运行的本脚本
echo;
goto end
:success
echo ^^操作完成，请在退出后继续执行安装程序
echo;
goto end
:not_necessary
echo;
echo ^hosts文件不存在，无需执行本操作，请在退出后直接执行安装程序
echo;
:end
pause