import os
import csv
import datetime
import subprocess


class GitController:
    """Gestisce la logica dei comandi Git, il registro CSV delle versioni e la struttura dei macro-moduli."""
    def __init__(self, manager):
        self.manager = manager

    @property
    def project_root(self):
        """Restituisce dinamicamente la cartella radice del progetto attualmente caricato."""
        root = getattr(self.manager, 'root_dir', None) or getattr(self.manager, 'project_root', None)
        if not root or not os.path.exists(root):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        return root

    @property
    def file_cronologia(self):
        """Restituisce il percorso del file CSV cercando sia in gestione_git/ sia nella radice."""
        p_sub = os.path.join(self.project_root, 'gestione_git', 'registro_sviluppo.csv')
        p_root = os.path.join(self.project_root, 'registro_sviluppo.csv')
        if os.path.exists(p_sub):
            return p_sub
        if os.path.exists(p_root):
            return p_root
        return p_sub

    @property
    def file_struttura_moduli(self):
        """Restituisce il percorso del file CSV di configurazione dei macro-moduli del progetto."""
        return os.path.join(self.project_root, 'gestione_git', 'struttura_moduli.csv')

    def ottieni_struttura_moduli(self):
        """Carica la lista dei macro-moduli dal CSV o ne auto-genera una basata sulle cartelle di applicazioni/."""
        moduli = []
        if os.path.exists(self.file_struttura_moduli) and os.path.getsize(self.file_struttura_moduli) > 0:
            try:
                with open(self.file_struttura_moduli, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    for riga in reader:
                        if riga and not riga[0].startswith('#'):
                            moduli.append(os.path.normpath(riga[0].strip()).replace("\\", "/"))
            except Exception as e:
                print(f"[ERRORE] Lettura struttura_moduli.csv: {e}")

        if not moduli:
            # Auto-generazione iniziale analizzando le sottocartelle di applicazioni/
            dir_app = os.path.join(self.project_root, 'applicazioni')
            if os.path.exists(dir_app):
                for elem in os.listdir(dir_app):
                    p_full = os.path.join(dir_app, elem)
                    if os.path.isdir(p_full) and not elem.startswith('.'):
                        moduli.append(f"applicazioni/{elem}")
            self.salva_struttura_moduli(moduli)

        return sorted(list(set(moduli)))

    def salva_struttura_moduli(self, lista_moduli):
        """Salva la lista aggiornata dei macro-moduli nel file CSV in gestione_git/."""
        try:
            os.makedirs(os.path.dirname(self.file_struttura_moduli), exist_ok=True)
            with open(self.file_struttura_moduli, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                for m in lista_moduli:
                    writer.writerow([m])
            return True
        except Exception as e:
            print(f"[ERRORE] Salvataggio struttura_moduli.csv: {e}")
            return False

    def ottieni_ultimo_git(self, rel_path):
        """Ottiene le informazioni sull'ultimo commit Git per un dato file."""
        try:
            cmd = ['git', 'log', '-1', '--format=%h - %s (%ad)', '--date=short', '--', rel_path]
            res = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return "-"

    def _carica_cache_git(self):
        """Carica la cache dell'ultimo git da un file CSV locale."""
        cache = {}
        cache_path = os.path.join(self.project_root, 'cache_ultimo_git.csv')
        if os.path.exists(cache_path):
            try:
                with open(cache_path, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) >= 2:
                            cache[row[0]] = row[1]
            except Exception:
                pass
        return cache

    def _salva_cache_git(self, cache):
        """Salva la cache dell'ultimo git nel file CSV locale."""
        cache_path = os.path.join(self.project_root, 'cache_ultimo_git.csv')
        try:
            with open(cache_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for path, commit in cache.items():
                    writer.writerow([path, commit])
        except Exception:
            pass

    def calcola_riepilogo_moduli(self, mappa_git):
        """Scansiona il file system sfruttando una cache CSV per l'ultimo git per garantire massima velocità."""
        moduli_def = self.ottieni_struttura_moduli()
        
        def crea_struttura_conteggi():
            return {'totale': 0, 'py': 0, 'cache': 0, 'dati': 0, 'cartelle_nuove': 0, 'file': []}

        riepilogo = {}
        for m in moduli_def:
            riepilogo[m] = {**crea_struttura_conteggi(), 'sub': {}}
        riepilogo['altri_file'] = {**crea_struttura_conteggi(), 'sub': {}}

        # Carichiamo la cache CSV dei commit precedenti
        cache_git = self._carica_cache_git()
        cache_modificata = False

        def da_escludere(percorso_relativo):
            parti = percorso_relativo.replace('\\', '/').split('/')
            for p in parti:
                if p.startswith('.') or p == '__pycache__':
                    return True
            return False

        root_dir = self.project_root
        if not root_dir or not os.path.exists(root_dir):
            return riepilogo

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']

            rel_dir = os.path.relpath(dirpath, root_dir)
            if rel_dir == '.':
                rel_dir = ''
            
            if rel_dir and da_escludere(rel_dir):
                continue

            for fname in filenames:
                if fname.startswith('.') or fname.endswith('.pyc'):
                    continue
                
                rel_path = os.path.join(rel_dir, fname).replace('\\', '/') if rel_dir else fname
                if da_escludere(rel_path):
                    continue

                stato = mappa_git.get(rel_path, "-")
                is_modificato = (stato != "-")
                
                # Gestione dell'ultimo git tramite cache CSV
                if stato == '??':
                    ultimo_git = "-"
                else:
                    if rel_path in cache_git:
                        ultimo_git = cache_git[rel_path]
                    else:
                        ultimo_git = self.ottieni_ultimo_git(rel_path)
                        cache_git[rel_path] = ultimo_git
                        cache_modificata = True
                
                modulo_trovato = None
                for m in moduli_def:
                    if rel_path == m or rel_path.startswith(m + "/"):
                        if modulo_trovato is None or len(m) > len(modulo_trovato):
                            modulo_trovato = m

                target = modulo_trovato if modulo_trovato else 'altri_file'
                
                is_cache = '__pycache__' in rel_path or rel_path.endswith('.pyc')
                is_py = rel_path.endswith('.py') and not is_cache

                riepilogo[target]['file'].append((rel_path, stato, ultimo_git))

                if is_modificato:
                    riepilogo[target]['totale'] += 1
                    if is_py:
                        riepilogo[target]['py'] += 1
                    elif is_cache:
                        riepilogo[target]['cache'] += 1
                    else:
                        riepilogo[target]['dati'] += 1

                if modulo_trovato:
                    sub_path = rel_path[len(modulo_trovato)+1:]
                else:
                    sub_path = rel_path

                parti_sub = sub_path.split('/')
                if len(parti_sub) > 1:
                    sub_dir = parti_sub[0]
                    if sub_dir not in riepilogo[target]['sub']:
                        riepilogo[target]['sub'][sub_dir] = crea_struttura_conteggi()
                    
                    riepilogo[target]['sub'][sub_dir]['file'].append((rel_path, stato, ultimo_git))
                    
                    if is_modificato:
                        riepilogo[target]['sub'][sub_dir]['totale'] += 1
                        if is_py:
                            riepilogo[target]['sub'][sub_dir]['py'] += 1
                        elif is_cache:
                            riepilogo[target]['sub'][sub_dir]['cache'] += 1
                        else:
                            riepilogo[target]['sub'][sub_dir]['dati'] += 1

                        if stato == '??':
                            riepilogo[target]['cartelle_nuove'] += 1
                            riepilogo[target]['sub'][sub_dir]['cartelle_nuove'] += 1

                elif stato == '??' and os.path.isdir(os.path.join(root_dir, rel_path)):
                    riepilogo[target]['cartelle_nuove'] += 1

        # Se sono stati trovati nuovi file da cachare, aggiorniamo il file CSV
        if cache_modificata:
            self._salva_cache_git(cache_git)

        return riepilogo

    def ottieni_mappa_stato_git(self):
        """Esegue git status e restituisce un dizionario {percorso_relativo: stato} per il progetto attivo."""
        try:
            cmd = ['git', 'status', '--porcelain', '-u']
            risultato = subprocess.check_output(cmd, text=True, cwd=self.project_root)
            mappa_git = {}
            for riga in risultato.splitlines():
                if riga.strip():
                    stato = riga[:2].strip()
                    file_p = os.path.normpath(riga[3:].strip()).replace("\\", "/")
                    mappa_git[file_p] = stato
            return mappa_git
        except Exception as e:
            print(f"[GIT-ERROR] Impossibile ricavare stato Git: {e}")
            return {}

    def ottieni_mappa_commit_specifico(self, tag_git_o_hash, lista_file_csv=""):
        """Ricava la mappa dei file modificati {percorso_relativo: stato} per uno specifico commit.
        Usa 'git show' se è presente l'hash, altrimenti va in fallback usando i file registrati nel CSV."""
        mappa_git = {}
        hash_commit = None

        if '(' in tag_git_o_hash and ')' in tag_git_o_hash:
            hash_commit = tag_git_o_hash.split('(')[1].split(')')[0].strip()

        if hash_commit:
            try:
                cmd = ['git', 'show', '--name-status', '--format=', hash_commit]
                risultato = subprocess.check_output(cmd, text=True, cwd=self.project_root)
                for riga in risultato.splitlines():
                    if riga.strip():
                        parti = riga.strip().split(maxsplit=1)
                        if len(parti) == 2:
                            stato = parti[0][0]
                            file_p = os.path.normpath(parti[1].strip()).replace("\\", "/")
                            mappa_git[file_p] = stato
                if mappa_git:
                    return mappa_git
            except Exception as e:
                print(f"[GIT-INFO] Impossibile usare git show per '{hash_commit}'. Uso fallback CSV.")

        if lista_file_csv and lista_file_csv != "Nessun file":
            file_list = [f.strip() for f in lista_file_csv.split(',') if f.strip()]
            for f in file_list:
                file_p = os.path.normpath(f).replace("\\", "/")
                mappa_git[file_p] = 'M'

        return mappa_git

    def esegui_commit(self, roadmap, argomenti, note):
        """Esegue il commit git e aggiorna il registro CSV del progetto attivo."""
        try:
            subprocess.run(['git', 'add', '.'], check=True, cwd=self.project_root)

            cmd = ['git', 'status', '--porcelain', '-u']
            risultato = subprocess.check_output(cmd, text=True, cwd=self.project_root)
            file_modificati = [riga[3:].strip() for riga in risultato.splitlines() if riga.strip()]
            str_file = ', '.join([os.path.basename(f) for f in file_modificati]) if file_modificati else "Nessun file"

            num_commits = subprocess.check_output(
                ['git', 'rev-list', '--count', 'HEAD'], text=True, cwd=self.project_root
            ).strip()
            tag_num = f"git {int(num_commits) + 1}"

            msg_commit = f"[{tag_num}] {roadmap}"
            subprocess.run(['git', 'commit', '-m', msg_commit], check=False, cwd=self.project_root)

            hash_commit = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD'], text=True, cwd=self.project_root
            ).strip()
            tag_git = f"{tag_num} ({hash_commit})"

            os.makedirs(os.path.dirname(self.file_cronologia), exist_ok=True)
            deve_intestazione = not os.path.exists(self.file_cronologia) or os.path.getsize(self.file_cronologia) == 0

            data_ora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            with open(self.file_cronologia, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                if deve_intestazione:
                    writer.writerow(['data / ora', 'roadmap', 'file modificati', 'argomenti', 'eventuali note', 'stato git'])
                writer.writerow([data_ora, roadmap, str_file, argomenti, note, tag_git])

            msg_successo = f"<b>Versione salvata con successo!</b><br><br>• Tag: <b>{tag_git}</b><br>• Registro CSV aggiornato."
            return True, msg_successo

        except Exception as err:
            return False, f"Si è verificato un errore durante il commit:\n{err}"

    def ottieni_cronologia_commit(self):
        """Legge il registro CSV delle versioni salvate e restituisce la lista dei commit con i relativi dettagli."""
        cronologia = []
        if os.path.exists(self.file_cronologia):
            try:
                with open(self.file_cronologia, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    next(reader, None)
                    for riga in reader:
                        if len(riga) >= 6:
                            cronologia.append({
                                'data': riga[0].strip(),
                                'roadmap': riga[1].strip(),
                                'file': riga[2].strip(),
                                'argomenti': riga[3].strip(),
                                'note': riga[4].strip(),
                                'tag_git': riga[5].strip()
                            })
            except Exception as e:
                print(f"[ERRORE] Lettura cronologia Git CSV: {e}")
        
        return list(reversed(cronologia))

    def esporta_progetto_usb(self, dest_dir, modalita="totale"):
        """Esporta il progetto su una chiavetta/cartella USB.
        modalita: 'totale' (tutto tranne cache/.venv/.git) o 'ultimo_commit' (solo i file dell'ultimo commit).
        """
        try:
            os.makedirs(dest_dir, exist_ok=True)
            file_da_esportare = []

            if modalita == "totale":
                # Scansiona tutto il progetto escludendo cartelle di sistema/cache
                def da_escludere(percorso_relativo):
                    parti = percorso_relativo.replace('\\', '/').split('/')
                    for p in parti:
                        if p.startswith('.') or p == '__pycache__' or p == '.venv' or p == 'env':
                            return True
                    return False

                for dirpath, dirnames, filenames in os.walk(self.project_root):
                    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__' and d != '.venv' and d != 'env']
                    rel_dir = os.path.relpath(dirpath, self.project_root)
                    if rel_dir == '.':
                        rel_dir = ''
                    if rel_dir and da_escludere(rel_dir):
                        continue

                    for fname in filenames:
                        if fname.endswith('.pyc') or fname.startswith('.'):
                            continue
                        rel_path = os.path.join(rel_dir, fname).replace('\\', '/') if rel_dir else fname
                        if not da_escludere(rel_path):
                            file_da_esportare.append(rel_path)

            elif modalita == "ultimo_commit":
                # Prende solo i file modificati nell'ultimo commit effettuato
                cmd = ['git', 'show', '--name-status', '--format=', 'HEAD']
                risultato = subprocess.check_output(cmd, text=True, cwd=self.project_root)
                for riga in risultato.splitlines():
                    if riga.strip():
                        parti = riga.strip().split(maxsplit=1)
                        if len(parti) == 2:
                            file_p = os.path.normpath(parti[1].strip()).replace("\\", "/")
                            if os.path.exists(os.path.join(self.project_root, file_p)):
                                file_da_esportare.append(file_p)
                
                if not file_da_esportare:
                    return False, "Nessun file trovato nell'ultimo commit!"

            # Esegue la copia fisica dei file replicando la struttura
            count = 0
            for rel_file in file_da_esportare:
                src_path = os.path.join(self.project_root, rel_file)
                dst_path = os.path.join(dest_dir, rel_file)
                if os.path.exists(src_path):
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    with open(src_path, 'rb') as f_src, open(dst_path, 'wb') as f_dst:
                        f_dst.write(f_src.read())
                    count += 1

            return True, f"Esportazione completata con successo!<br>• File copiati: <b>{count}</b><br>• Destinazione: {dest_dir}"

        except Exception as e:
            return False, f"Errore durante l'esportazione USB:\n{e}"

    def importa_progetto_usb(self, src_dir):
        """Importa/sincronizza i file da una cartella USB al progetto corrente."""
        try:
            if not os.path.exists(src_dir):
                return False, "La cartella di origine selezionata non esiste!"

            count = 0
            for dirpath, dirnames, filenames in os.walk(src_dir):
                dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__' and d != '.venv']
                rel_dir = os.path.relpath(dirpath, src_dir)
                if rel_dir == '.':
                    rel_dir = ''

                for fname in filenames:
                    if fname.endswith('.pyc') or fname.startswith('.'):
                        continue
                    rel_file = os.path.join(rel_dir, fname).replace('\\', '/') if rel_dir else fname
                    
                    src_file = os.path.join(dirpath, fname)
                    dst_file = os.path.join(self.project_root, rel_file)

                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    with open(src_file, 'rb') as f_src, open(dst_file, 'wb') as f_dst:
                        f_dst.write(f_src.read())
                    count += 1

            return True, f"Sincronizzazione completata!<br>• File aggiornati/importati: <b>{count}</b>"

        except Exception as e:
            return False, f"Errore durante l'importazione USB:\n{e}"

