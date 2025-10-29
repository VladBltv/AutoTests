#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
import paramiko
import requests


def run_mmdc(input_file: Path, output_file: Path, fmt: str, width: int = None, height: int = None):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    mmdc_cmd = 'mmdc.cmd' if os.name == 'nt' else 'mmdc'
    
    cmd = [
        mmdc_cmd,
        '-i', str(input_file),
        '-o', str(output_file)
    ]
    if fmt.lower() == 'png':
        cmd += ['-b', 'transparent']
        if width:
            cmd += ['-w', str(width)]
        if height:
            cmd += ['-H', str(height)]
    elif fmt.lower() == 'svg':
        pass
    else:
        raise ValueError('Формат не поддерживается. Используйте svg или png')

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, shell=True)
    except FileNotFoundError:
        raise RuntimeError('mmdc не найден. Установить: npm install -g @mermaid-js/mermaid-cli')


def validate_mermaid_file(file_path: Path) -> bool:
    """Проверяет что файл является валидным Mermaid файлом"""
    try:
        content = file_path.read_text(encoding='utf-8').strip()
        # Базовая проверка: файл не пустой и содержит ключевые слова Mermaid
        if not content:
            print(f"Предупреждение: файл пустой: {file_path.name}")
            return False
        
        # Проверка на наличие Mermaid синтаксиса (graph, flowchart, sequenceDiagram и т.д.)
        mermaid_keywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                          'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitgraph']
        if not any(keyword in content for keyword in mermaid_keywords):
            print(f"Предупреждение: файл не содержит Mermaid синтаксис: {file_path.name}")
            return False
        
        return True
    except Exception as e:
        print(f"Ошибка чтения файла {file_path.name}: {e}")
        return False


def find_mermaid_files(source_dir: Path, pattern: str) -> List[Path]:
    """Находит все Mermaid файлы с валидацией"""
    all_files = sorted(source_dir.rglob(pattern))
    validated_files = []
    
    for file_path in all_files:
        if validate_mermaid_file(file_path):
            validated_files.append(file_path)
        else:
            print(f"Пропущен невалидный файл: {file_path.name}")
    return validated_files


def upload_file_sftp(
    sftp: paramiko.SFTPClient,
    local_path: Path,
    remote_dir: str,
    remote_filename: str
) -> tuple:
    """Загружает файл на SFTP сервер"""
    remote_path = f"{remote_dir.rstrip('/')}/{remote_filename}"
    
    # Проверяем существует ли файл на сервере
    file_exists = False
    try:
        sftp.stat(remote_path)
        file_exists = True
    except IOError:
        pass
    
    # Загружаем файл (перезаписывает если существует)
    sftp.put(str(local_path), remote_path)
    
    return remote_path, file_exists


def connect_sftp(host: str, port: int, user: str, password: str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=port, username=user, password=password, timeout=30, look_for_keys=False, allow_agent=False)
    return ssh, ssh.open_sftp()


def build_public_url(base: str, remote_path: str, remote_root: str) -> str:
    rp = remote_path
    rr = remote_root.rstrip('/')
    if rp.startswith(rr):
        suffix = rp[len(rr):]
    else:
        suffix = '/' + Path(rp).name
    return (base.rstrip('/') + suffix).replace('///', '/').replace('//', '/', 1)


def get_file_hash(file_path: Path) -> str:
    """Вычисляет MD5 хэш файла для определения изменений"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def load_hash_cache() -> Dict[str, str]:
    """Загружает кэш хэшей файлов из .diagram_hashes.json"""
    cache_file = Path('.diagram_hashes.json')
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_hash_cache(cache: Dict[str, str]):
    """Сохраняет кэш хэшей файлов"""
    cache_file = Path('.diagram_hashes.json')
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')


def validate_cdn_path(path: str) -> bool:
    """
    Проверяет что путь корректен для CDN
    """
    if not path:
        print("Пустой путь для CDN")
        return False
    
    # Проверка расширения
    ext = Path(path).suffix.lower()
    if not ext:
        print(f"Файл без расширения: {path}")
        return False
    
    allowed_extensions = {'.png', '.svg', '.jpg', '.jpeg', '.gif', '.webp'}
    if ext not in allowed_extensions:
        print(f"Неизвестное расширение {ext} в файле: {path}")
    
    return True


def normalize_cdn_path(remote_path: str, prefix_to_remove: str) -> str:
    """
    Преобразует SFTP путь в CDN путь
    
    /data/public/misc-content/befree/diagrams/test.png
    → misc-content/befree/diagrams/test.png
    """
    cdn_path = remote_path
    
    # Убираем префикс
    if prefix_to_remove and cdn_path.startswith(prefix_to_remove):
        cdn_path = cdn_path[len(prefix_to_remove):]
    
    # Убираем ведущий слэш
    cdn_path = cdn_path.lstrip('/')
    
    return cdn_path


def get_cdn_oauth_token(oauth_url: str, client_id: str, client_secret: str) -> Optional[str]:
    """Получает OAuth токен для API CDN"""
    try:
        response = requests.post(
            oauth_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            },
            timeout=10
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data.get('access_token')
    except Exception as e:
        print(f"Ошибка получения OAuth токена: {e}")
        return None


def invalidate_cdn_cache(paths: List[str], api_url: str, token: str) -> bool:
    """
    Отправляет запрос на инвалидацию кэша CDN
    
    paths: ['misc-content/befree/diagrams/test.png', ...]
    """
    if not paths:
        print("Нет файлов для инвалидации CDN")
        return True
    
    # Валидация всех путей
    valid_paths = []
    for path in paths:
        if validate_cdn_path(path):
            valid_paths.append(path)
    
    if not valid_paths:
        print("Нет валидных путей для инвалидации CDN")
        return False
    
    try:
        print(f"\nОтправка запроса на инвалидацию CDN для {len(valid_paths)} файлов...")
        
        response = requests.post(
            api_url,
            json={'paths': valid_paths},
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            timeout=30
        )
        response.raise_for_status()
        
        print(f"CDN инвалидация успешно запущена для {len(valid_paths)} файлов")
        for path in valid_paths:
            print(f"   - {path}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка инвалидации CDN: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Ответ сервера: {e.response.text}")
        return False


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description='Render Mermaid diagrams and upload to SFTP')
    parser.add_argument('--source-dir', default=os.getenv('SOURCE_DIR', 'sequences'))
    parser.add_argument('--pattern', default=os.getenv('PATTERN', '*.mermaid'))
    parser.add_argument('--format', default=os.getenv('OUTPUT_FORMAT', 'png'), choices=['png', 'svg'])
    parser.add_argument('--remote-dir', default=os.getenv('SFTP_REMOTE_DIR', '/upload/diagrams'))
    parser.add_argument('--url-base', default=os.getenv('SFTP_REMOTE_HTTP_BASE', ''))
    parser.add_argument('--width', type=int, default=int(os.getenv('OUTPUT_WIDTH', '0') or 0))
    parser.add_argument('--height', type=int, default=int(os.getenv('OUTPUT_HEIGHT', '0') or 0))
    parser.add_argument('--dry-run', action='store_true', help='Только генерация PNG, без загрузки на SFTP')

    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    
    # Проверка что директория существует
    if not source_dir.exists():
        raise SystemExit(f'Директория не найдена: {source_dir}')
    
    # Проверка что директория не пустая
    all_files_in_dir = list(source_dir.rglob('*'))
    if not all_files_in_dir:
        raise SystemExit(f'Директория пустая: {source_dir}')
    
    # Поиск и валидация Mermaid файлов
    files = find_mermaid_files(source_dir, args.pattern)
    if not files:
        raise SystemExit(f'Не найдено валидных Mermaid файлов (*.mermaid) в директории: {source_dir}')
    
    print(f'\nНайдено {len(files)} валидных Mermaid файлов для обработки:')
    for f in files:
        print(f'   - {f.name}')

    if not args.dry_run:
        sftp_host = os.getenv('SFTP_HOST')
        # sftp_port = int(os.getenv('SFTP_PORT', '22'))
        sftp_user = os.getenv('SFTP_USER')
        sftp_password = os.getenv('SFTP_PASSWORD')

        if not all([sftp_host, sftp_user, sftp_password]):
            raise SystemExit('Нет переменных окружения: SFTP_HOST, SFTP_USER, SFTP_PASSWORD')

    width = args.width or None
    height = args.height or None

    # Загружаем кэш хэшей для отслеживания изменений
    hash_cache = load_hash_cache()

    # Режим dry-run: только генерация без загрузки
    if args.dry_run:
        print('\nРЕЖИМ DRY-RUN: Только генерация PNG, без загрузки на SFTP\n')
        results: List[Dict[str, str]] = []
        for f in files:
            out_ext = '.png' if args.format == 'png' else '.svg'
            out_file = f.with_suffix(out_ext)
            
            run_mmdc(f, out_file, args.format, width, height)
            print(f'Сгенерирован: {out_file}')
            
            # Обновляем хэш в кэше
            current_hash = get_file_hash(out_file)
            hash_cache[out_file.name] = current_hash
            
            remote_path = f"{args.remote_dir.rstrip('/')}/{out_file.name}"
            url = build_public_url(args.url_base, remote_path, args.remote_dir) if args.url_base else ''
            
            results.append({
                'source': str(f),
                'local_image': str(out_file),
                'remote_path': f'{remote_path} (НЕ ЗАГРУЖЕН - DRY RUN)',
                'public_url': f'{url} (НЕ ЗАГРУЖЕН - DRY RUN)' if url else ''
            })
        
        save_hash_cache(hash_cache)
        manifest_path = Path('upload_results.json')
        manifest_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'\nРезультаты сохранены в: {manifest_path.resolve()}')
        print('\nФайлы НЕ были загружены на SFTP (dry-run режим)')
        return

    # Обычный режим: генерация + загрузка
    sftp_host = os.getenv('SFTP_HOST')
    sftp_port = int(os.getenv('SFTP_PORT', '22'))
    sftp_user = os.getenv('SFTP_USER')
    sftp_password = os.getenv('SFTP_PASSWORD')
    
    ssh, sftp = connect_sftp(sftp_host, sftp_port, sftp_user, sftp_password)

    results: List[Dict[str, str]] = []
    changed_files_for_cdn = []  # Файлы для инвалидации CDN
    
    try:
        for f in files:
            out_ext = '.png' if args.format == 'png' else '.svg'
            out_file = f.with_suffix(out_ext)

            run_mmdc(f, out_file, args.format, width, height)
            
            # Проверяем изменился ли файл по хэшу
            current_hash = get_file_hash(out_file)
            cached_hash = hash_cache.get(out_file.name)
            file_changed = (cached_hash != current_hash)

            remote_filename = out_file.name
            
            # Загружаем ТОЛЬКО если файл изменился или это новый файл
            if file_changed:
                remote_path, file_existed = upload_file_sftp(sftp, out_file, args.remote_dir, remote_filename)
                
                # Обновляем хэш в кэше
                hash_cache[out_file.name] = current_hash

                url = ''
                if args.url_base:
                    url = build_public_url(args.url_base, remote_path, args.remote_dir)

                # Показываем статус загрузки
                if file_existed:
                    print(f'🔄 Перезаписан на SFTP: {remote_path}')
                else:
                    print(f'✅ Загружен на SFTP: {remote_path}')
                
                # Добавляем в список для инвалидации CDN
                cdn_path_prefix = os.getenv('CDN_PATH_PREFIX', '/data/public/')
                cdn_path = normalize_cdn_path(remote_path, cdn_path_prefix)
                changed_files_for_cdn.append(cdn_path)

                results.append({
                    'source': str(f),
                    'local_image': str(out_file),
                    'remote_path': remote_path,
                    'public_url': url,
                    'action': 'overwritten' if file_existed else 'created',
                    'cdn_invalidated': True
                })
            else:
                # Файл не изменился - пропускаем загрузку
                remote_path = f"{args.remote_dir.rstrip('/')}/{remote_filename}"
                url = ''
                if args.url_base:
                    url = build_public_url(args.url_base, remote_path, args.remote_dir)
                
                print(f'Пропущен: {out_file.name}')
                
                results.append({
                    'source': str(f),
                    'local_image': str(out_file),
                    'remote_path': remote_path,
                    'public_url': url,
                    'action': 'skipped',
                    'cdn_invalidated': False
                })

    finally:
        try:
            sftp.close()
        except Exception:
            pass
        try:
            ssh.close()
        except Exception:
            pass

    # Сохраняем обновленный кэш хэшей
    save_hash_cache(hash_cache)
    
    # Инвалидация CDN если включена
    cdn_enabled = os.getenv('CDN_INVALIDATE_ENABLED', 'false').lower() == 'true'
    if cdn_enabled and changed_files_for_cdn:
        print(f"\nCDN инвалидация включена, обрабатываем {len(changed_files_for_cdn)} измененных файлов...")
        
        # Получаем OAuth токен
        oauth_url = os.getenv('CDN_OAUTH_URL')
        client_id = os.getenv('CDN_CLIENT_ID')
        client_secret = os.getenv('CDN_CLIENT_SECRET')
        invalidate_url = os.getenv('CDN_INVALIDATE_URL')
        
        if all([oauth_url, client_id, client_secret, invalidate_url]):
            token = get_cdn_oauth_token(oauth_url, client_id, client_secret)
            if token:
                invalidate_cdn_cache(changed_files_for_cdn, invalidate_url, token)
            else:
                print("Не удалось получить токен, пропускаем инвалидацию CDN")
        else:
            print("CDN параметры не полностью настроены в .env")
    elif cdn_enabled and not changed_files_for_cdn:
        print("\nНет измененных файлов для инвалидации CDN")

    manifest_path = Path('upload_results.json')
    manifest_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\nРезультаты сохранены в: {manifest_path.resolve()}')


if __name__ == '__main__':
    main()
