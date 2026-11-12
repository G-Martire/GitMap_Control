from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtWidgets import QTreeWidgetItem


def conta_modifiche_subtree(tree_node):
    """Conta ricorsivamente le modifiche all'interno di un sotto-albero."""
    count = 0
    for _, _, stato, _ in tree_node['files']:
        if stato != "-":
            count += 1
    for dname in tree_node['dirs']:
        count += conta_modifiche_subtree(tree_node['dirs'][dname])
    return count


def popola_nodo_ricorsivo(parent_item, tree_node):
    """Popola ricorsivamente l'albero dei file e delle cartelle."""
    # 1. Cartelle prima (ordinate alfabeticamente)
    for dname in sorted(tree_node['dirs'].keys()):
        child_tree = tree_node['dirs'][dname]
        mod_count = conta_modifiche_subtree(child_tree)
        etichetta = f"📂 {dname} (Mod: {mod_count})" if mod_count > 0 else f"📂 {dname} (Pulita)"
        sub_item = QTreeWidgetItem([etichetta, "", ""])
        parent_item.addChild(sub_item)
        popola_nodo_ricorsivo(sub_item, child_tree)

    # 2. File poi (ordinati alfabeticamente)
    for fname, file_path, stato, ultimo_git in sorted(tree_node['files'], key=lambda x: x[0]):
        icona_file = "🐍" if file_path.endswith('.py') else "📄"
        is_modificato = (stato != "-")
        testo_stato = f"Stato: {stato}" if is_modificato else ""
        
        file_item = QTreeWidgetItem([f"   {icona_file} {fname}", testo_stato, ultimo_git])
        
        if is_modificato:
            colore_mod = QColor(0, 102, 204) if stato == 'M' else QColor(0, 128, 0)
            for c in range(3):
                file_item.setForeground(c, QBrush(colore_mod))
                file_item.setFont(c, QFont("Segoe UI", 9, QFont.Weight.Bold))
        else:
            file_item.setForeground(2, QBrush(QColor(120, 120, 120)))

        parent_item.addChild(file_item)


def controlla_e_espandi(item):
    """Espande ricorsivamente solo i nodi che contengono modifiche o stati attivi."""
    ha_modifiche_figli = False
    for i in range(item.childCount()):
        child = item.child(i)
        if controlla_e_espandi(child):
            ha_modifiche_figli = True
    
    testo_col1 = item.text(1)
    testo_col0 = item.text(0)
    is_modificato = "Stato:" in testo_col1 or "Mod:" in testo_col0 and "(Mod: 0)" not in testo_col0
    
    if is_modificato or ha_modifiche_figli:
        item.setExpanded(True)
        return True
    else:
        item.setExpanded(False)
        return False

