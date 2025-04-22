#!/bin/bash
# Sentaurus SWB 自动化仿真环境安装脚本

# 获取安装包根目录
PACKAGE_DIR=$(cd "$(dirname "$0")"; pwd)
echo "安装包根目录: $PACKAGE_DIR"

# 创建日志文件
LOG_FILE="$PACKAGE_DIR/install.log"
echo "安装日志将保存到: $LOG_FILE"
echo "安装开始于: $(date)" > $LOG_FILE

# 为Python 3.11安装必要的依赖库
echo "正在安装Python 3.11的依赖..."
{
    sudo yum -y install gcc gcc-c++ make zlib zlib-devel libffi-devel bzip2-devel ncurses-devel openssl-devel
} >> $LOG_FILE 2>&1

# 创建目标目录
TARGET_DIR="$HOME/sentaurus_auto"
mkdir -p $TARGET_DIR
echo "项目将安装到: $TARGET_DIR"

# 复制项目文件
echo "正在复制项目文件..."
cp -r $PACKAGE_DIR/project_files/* $TARGET_DIR/
echo "项目文件已复制到 $TARGET_DIR" | tee -a $LOG_FILE

# 创建Python虚拟环境
echo "创建Python虚拟环境..."
cd $TARGET_DIR
python3.11 -m venv swb_env
source swb_env/bin/activate
echo "Python虚拟环境已创建: $TARGET_DIR/swb_env" | tee -a $LOG_FILE

# 安装依赖包
echo "安装依赖包..."
pip install --upgrade pip >> $LOG_FILE 2>&1

# 安装wheel文件
echo "安装SWB依赖包..."
pip install $PACKAGE_DIR/wheels/rayuela-4.0.0-py3-none-any.whl >> $LOG_FILE 2>&1
pip install $PACKAGE_DIR/wheels/swbutils-1.1.4-cp311-none-linux_x86_64.whl >> $LOG_FILE 2>&1
pip install $PACKAGE_DIR/wheels/swbpy2-2.2.0-cp311-none-linux_x86_64.whl >> $LOG_FILE 2>&1
echo "SWB依赖包已安装" | tee -a $LOG_FILE

# 安装其他依赖
echo "安装其他Python依赖..."
pip install requests matplotlib pandas numpy >> $LOG_FILE 2>&1
echo "Python依赖已安装" | tee -a $LOG_FILE

# 创建启动脚本
echo "创建启动脚本..."
cat > $TARGET_DIR/run_swb_auto.sh << EOL
#!/bin/bash
# Sentaurus SWB 自动化仿真脚本

# 获取项目根目录
PROJECT_DIR=\$(cd "\$(dirname "\$0")"; pwd)
echo "项目根目录: \$PROJECT_DIR"

# 激活Python虚拟环境
source \$PROJECT_DIR/swb_env/bin/activate

# 设置环境变量
export PYTHONIOENCODING=UTF-8

# 加载Sentaurus环境
source \$PROJECT_DIR/MCT-SEE-Normal-Old/sentaurus_env.sh

# 进入项目目录
cd \$PROJECT_DIR/MCT-SEE-Normal-Old

# 运行自动化脚本
python3.11 auto_sim/auto_sim_main.py --config auto_sim_config.json --project .

# 退出虚拟环境
deactivate
EOL

chmod +x $TARGET_DIR/run_swb_auto.sh
echo "启动脚本已创建: $TARGET_DIR/run_swb_auto.sh" | tee -a $LOG_FILE

# 安装完成
echo "" | tee -a $LOG_FILE
echo "安装已完成!" | tee -a $LOG_FILE
echo "使用以下命令运行自动化系统:" | tee -a $LOG_FILE
echo "  cd $TARGET_DIR" | tee -a $LOG_FILE
echo "  ./run_swb_auto.sh" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "安装结束于: $(date)" >> $LOG_FILE 