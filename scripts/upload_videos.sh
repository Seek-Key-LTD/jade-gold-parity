#!/bin/bash

# 视频上传到 Cloudflare R2 脚本
# 使用方法: ./scripts/upload_videos.sh [视频目录]

set -e

# 配置信息 - 需要您填入实际的值
R2_BUCKET="your-bucket-name"
R2_ACCOUNT_ID="your-account-id"
R2_ACCESS_KEY="your-access-key"
R2_SECRET_KEY="your-secret-key"
R2_ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# 视频目录 (默认为 static/videos)
VIDEO_DIR=${1:-"static/videos"}

# 公共访问域名 (需要配置 R2 自定义域名)
PUBLIC_DOMAIN="https://your-cdn-domain.com"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否安装了 AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}错误: 未找到 AWS CLI，请先安装 AWS CLI${NC}"
    echo "安装命令: pip install awscli"
    exit 1
fi

# 检查视频目录是否存在
if [ ! -d "$VIDEO_DIR" ]; then
    echo -e "${RED}错误: 视频目录 $VIDEO_DIR 不存在${NC}"
    exit 1
fi

# 配置 AWS CLI for R2
aws configure set aws_access_key_id $R2_ACCESS_KEY
aws configure set aws_secret_access_key $R2_SECRET_KEY
aws configure set default.region auto

echo -e "${YELLOW}开始上传视频到 Cloudflare R2...${NC}"

# 创建上传日志
UPLOAD_LOG="uploads_$(date +%Y%m%d_%H%M%S).log"
echo "视频上传日志 - $(date)" > $UPLOAD_LOG

# 遍历视频目录中的所有文件
find "$VIDEO_DIR" -type f \( -name "*.mp4" -o -name "*.webm" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" \) | while read video_file; do
    
    # 获取相对路径
    relative_path=${video_file#$VIDEO_DIR/}
    
    # 获取文件信息
    file_size=$(du -h "$video_file" | cut -f1)
    file_name=$(basename "$video_file")
    
    echo -e "${GREEN}上传: $file_name ($file_size)${NC}"
    
    # 上传文件到 R2
    if aws s3 cp "$video_file" "s3://$R2_BUCKET/videos/$relative_path" \
        --endpoint-url "$R2_ENDPOINT" \
        --content-type "$(get_mime_type "$video_file")" \
        --no-progress >> $UPLOAD_LOG 2>&1; then
        
        # 生成公共链接
        public_url="$PUBLIC_DOMAIN/videos/$relative_path"
        
        echo -e "${GREEN}✅ 成功: $file_name${NC}"
        echo -e "   公共链接: ${YELLOW}$public_url${NC}"
        
        # 记录成功日志
        echo "SUCCESS: $video_file -> $public_url" >> $UPLOAD_LOG
        
        # 将链接保存到映射文件
        echo "$relative_path|$public_url" >> video_url_mapping.txt
        
    else
        echo -e "${RED}❌ 失败: $file_name${NC}"
        echo "FAILED: $video_file" >> $UPLOAD_LOG
    fi
done

echo -e "${GREEN}上传完成！${NC}"
echo "详细日志: $UPLOAD_LOG"
echo "URL 映射: video_url_mapping.txt"

# 获取 MIME 类型的辅助函数
get_mime_type() {
    local file="$1"
    local extension="${file##*.}"
    
    case "$extension" in
        mp4) echo "video/mp4" ;;
        webm) echo "video/webm" ;;
        mov) echo "video/quicktime" ;;
        avi) echo "video/x-msvideo" ;;
        mkv) echo "video/x-matroska" ;;
        *) echo "application/octet-stream" ;;
    esac
}

echo -e "${YELLOW}提示: 请确保已在 Cloudflare R2 中配置自定义域名以获得公共访问权限${NC}"