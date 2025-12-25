#!/bin/bash

set -e

R2_BUCKET="arxiv-media"
R2_ENDPOINT="your-r2-endpoint.r2.cloudflarestorage.com"
CDN_DOMAIN="cdn.yourdomain.com"

echo "开始上传NotebookLM内容到R2..."

echo "上传NotebookLM视频..."
for file in media/notebooklm/**/video/*; do
  if [ -f "$file" ]; then
    rel_path=${file#media/}
    echo "上传: $file"
    aws s3 cp "$file" "s3://$R2_BUCKET/$rel_path" \
      --endpoint-url "https://$R2_ENDPOINT" \
      --acl public-read \
      --content-type "video/mp4"
    echo "$file,https://$CDN_DOMAIN/$rel_path" >> media/notebooklm-mapping.csv
  fi
done

echo "上传NotebookLM音频..."
for file in media/notebooklm/**/audio/*; do
  if [ -f "$file" ]; then
    rel_path=${file#media/}
    echo "上传: $file"
    aws s3 cp "$file" "s3://$R2_BUCKET/$rel_path" \
      --endpoint-url "https://$R2_ENDPOINT" \
      --acl public-read \
      --content-type "audio/mpeg"
    echo "$file,https://$CDN_DOMAIN/$rel_path" >> media/notebooklm-mapping.csv
  fi
done

echo "上传信息图..."
for file in media/notebooklm/**/infographics/*; do
  if [ -f "$file" ]; then
    rel_path=${file#media/}
    echo "上传: $file"
    aws s3 cp "$file" "s3://$R2_BUCKET/$rel_path" \
      --endpoint-url "https://$R2_ENDPOINT" \
      --acl public-read
    echo "$file,https://$CDN_DOMAIN/$rel_path" >> media/notebooklm-mapping.csv
  fi
done

echo "NotebookLM内容上传完成！"
echo "链接映射表已保存到: media/notebooklm-mapping.csv"
