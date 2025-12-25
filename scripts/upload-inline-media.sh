#!/bin/bash

set -e

R2_BUCKET="arxiv-media"
R2_ENDPOINT="your-r2-endpoint.r2.cloudflarestorage.com"
CDN_DOMAIN="cdn.yourdomain.com"

echo "开始上传辅助性媒体文件到R2..."

echo "上传辅助性图片..."
for file in media/inline/images/**/*; do
  if [ -f "$file" ]; then
    rel_path=${file#media/}
    echo "上传: $file"
    aws s3 cp "$file" "s3://$R2_BUCKET/$rel_path" \
      --endpoint-url "https://$R2_ENDPOINT" \
      --acl public-read
    echo "$file,https://$CDN_DOMAIN/$rel_path" >> media/inline-mapping.csv
  fi
done

echo "上传PDF文件..."
for file in media/inline/pdfs/**/*; do
  if [ -f "$file" ]; then
    rel_path=${file#media/}
    echo "上传: $file"
    aws s3 cp "$file" "s3://$R2_BUCKET/$rel_path" \
      --endpoint-url "https://$R2_ENDPOINT" \
      --acl public-read
    echo "$file,https://$CDN_DOMAIN/$rel_path" >> media/inline-mapping.csv
  fi
done

echo "辅助性媒体文件上传完成！"
echo "链接映射表已保存到: media/inline-mapping.csv"
