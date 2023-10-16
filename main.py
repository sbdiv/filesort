import re  
import shutil 
import sys
from pathlib import Path
import os



CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "u", "ya", "ye", "yi", "g")


Trans = dict()
for cyr, lat in zip(CYRILLIC_SYMBOLS,TRANSLATION):
    Trans[ord(cyr)] = lat
    Trans[ord(cyr.upper())] = lat.upper()


def normalize(name):
    base, ext = os.path.splitext(name) #розділення на імя та розширення
    base = re.sub(r'(?![()a-zA-Z0-9])', '_', base.translate(Trans))# переклад імені
    return f'{base}{ext}' #повернення повного ім'я та розширення


def list_files_in_directory(PATH):
    file_list = []

    for path in Path(PATH).rglob('*'): #рекрусивне проходження по файлам
        if path.is_file(): #перевірка на файл
            new_path = path.parent / normalize(path.name) #затосовуюмо переклад з кри на лат та міняємо шлях до файлу
            path.rename(new_path) #перейменовуємо файл
            file_list.append((new_path.name, new_path)) #записуємо в лист кортеджів файл та шлях

    return file_list



def rename_files(file_list):
    file_name_counts = {} # словник, що підраховує кількість файлів з однаковим ім'ям
    new_file_list = [] # новий список кортежів імен файлів та шляхів
    
    for file_name, file_path in file_list:
        base_name, ext = os.path.splitext(file_name) # розбиваємо ім'я на назву та розширення
        if file_name in file_name_counts: # якщо файл в словнику, збільшуємо кількість в словниуц на 1 та зберігаємо як (1)(2) і тд
            file_name_counts[file_name] += 1
            new_file_name = f"{base_name}({file_name_counts[file_name]}){ext}"
        else: #якщо ні залишаємо без змін
            file_name_counts[file_name] = 0  
            new_file_name = file_name
        
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name) #новий шлях до файлу
        new_file_list.append((new_file_name, new_file_path)) #запис у список кортеджів
    
    return new_file_list




def compare_and_rename(file_list, new_file_list):

     for (name, path), (new_name, new_path) in zip(file_list, new_file_list): # пробігаємось по двух списках
 
       if name != new_name: # якщо імена різні змінюємо ім'я файлу на те що в new_file_list
            path.rename(path.with_name(new_name))
        
folder_names = ('images','video','documents','audio','archives','unknown')  #імена папок     


def add_new_folders(PATH,folder_names):
    
    folder_paths = {}   #словник який складається з імен папок та їх шляхом
    for folder_name in folder_names:    #створення папок та занесення їх до словника
        folder_path = os.path.join(PATH, folder_name)
        os.makedirs(folder_path,exist_ok=True)
        folder_paths[folder_name] = folder_path
    return folder_paths

def del_folders(PATH):
    all_dirs=os.listdir(PATH) # отримуємо повний список директорій

    for item in all_dirs:
        item_path = os.path.join(PATH,item) #формуємо шлях до папки
        if os.path.isdir(item_path) and item not in folder_names: #якщо є така папка, та її немає у списку видаляємо її
             shutil.rmtree(item_path)


def archives_unpack(PATH): #ця функція розпаковує архіви тільки типу (zip, tar, tar.gz, tar.bz2, tar.xz)
    ARCHIVES_PATH = Path(PATH) / 'archives' #шлях до папки з архівами
    for archive_file in ARCHIVES_PATH.iterdir():#перебираємо архіви
        if archive_file.is_file() and archive_file.suffix in ('.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz'): #якщо є такий та він такого формату які перелічені в списку
            new_archive_path = ARCHIVES_PATH / archive_file.stem #новий шлях до архіву
            new_archive_path.mkdir(parents=True, exist_ok=True) #створюємо папку куди буде розпаковуватись архів
            shutil.unpack_archive(archive_file, new_archive_path) #розпаковуємо архів

    
            
def sort_folders(PATH):
        #кортеджи розширень
        images = ('JPEG', 'PNG', 'JPG', 'SVG')
        video =('AVI', 'MP4', 'MOV', 'MKV')
        doc=('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
        audio=('MP3', 'OGG', 'WAV', 'AMR')
        arch=('ZIP', 'GZ', 'TAR','RAR')
        known_ext = []
        unknown_ext = []

        old_file_list=list_files_in_directory(PATH) #отримуємо список файлів
        new_file_list = rename_files(old_file_list) #отримуємо новий список файлів
        compare_and_rename(old_file_list,new_file_list) #перейменовуємо однакові файли
        folder_path= add_new_folders(PATH,folder_names) #створюємо потрібні папки

        for file_name, file_path in new_file_list: #перебираємо імена та шляхи
            filename, fileext = os.path.splitext(file_name) #розділяємо імя на розширення та назву
            file_ext = fileext[1:].upper()      #отримуємо розширення
            if file_ext in images: #сотруємо по папках
                known_ext.append(file_ext)
                shutil.move(file_path,folder_path['images'])
            elif file_ext in video:
                known_ext.append(file_ext)
                shutil.move(file_path,folder_path['video'])
            elif file_ext in doc:
                known_ext.append(file_ext)
                shutil.move(file_path,folder_path['documents'])
            elif file_ext in audio:
                known_ext.append(file_ext)
                shutil.move(file_path,folder_path['audio'])
            elif file_ext in arch: 
                known_ext.append(file_ext)
                shutil.move(file_path,folder_path['archives'])
            else: 
                unknown_ext.append(file_ext)
                shutil.move(file_path,folder_path['unknown'])

        del_folders(PATH) #видаляємо непотрібні папки
        archives_unpack(PATH)# розпаковуємо архіви

        #виводимо відомі і невідомі розширення
        print(f'Відомі розширення:{known_ext}')
        print(f'Невідомі розширення:{unknown_ext}')
        

    
        
        

if __name__ == "__main__":
    folder_process = Path(sys.argv[1])
    sort_folders(folder_process.resolve())