import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class DateMaskEntry(tk.Entry):
    """
    Componente reutilizável de Entry do Tkinter com máscara de data no formato DD/MM/AAAA.
    Focado em uma experiência de digitação fluida e robusta:
    - Permite apenas números.
    - Insere as barras '/' automaticamente.
    - Limita a entrada a 8 dígitos numéricos.
    - Suporta Backspace de forma fluida (sem travar na exclusão das barras).
    - Mantém a estabilidade da posição do cursor.
    - Fornece validação lógica para datas reais (evitando dias/meses inválidos).
    """
    def __init__(self, master=None, **kwargs):
        self.var = tk.StringVar()
        kwargs['textvariable'] = self.var
        super().__init__(master, **kwargs)
        
        if 'width' not in kwargs:
            self.configure(width=12)
            
        # Liga os eventos de teclado
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<BackSpace>", self._on_backspace)
        self.var.trace_add("write", self._format_date)
        
        self._updating = False
        self._digits = ""

    def _on_key_press(self, event):
        # Permitir atalhos de controle (como Ctrl+C, Ctrl+V, Setas, Tab, etc.)
        if event.state & 4:  # Ctrl pressionado no Windows/Linux
            return
        if event.keysym in ("Left", "Right", "Up", "Down", "Tab", "Return", "Escape", "Home", "End"):
            return
            
        # Rejeitar qualquer tecla que não seja um número
        if event.char and not event.char.isdigit():
            return "break"
            
        # Limitar a entrada a 8 dígitos numéricos (exceto se houver texto selecionado sendo substituído)
        if len(self._digits) >= 8 and not self.select_present():
            return "break"

    def _on_backspace(self, event):
        """Tratamento especial de Backspace para evitar travamento ao apagar a barra '/'."""
        if self.select_present():
            # Se houver texto selecionado, permite o comportamento padrão de remoção
            return
            
        cursor_pos = self.index(tk.INSERT)
        if cursor_pos > 0:
            current_text = self.get()
            # Se o caractere logo antes do cursor for uma barra, apagamos ela E o dígito numérico anterior
            if current_text[cursor_pos - 1] == "/":
                self._updating = True
                # Corta a barra e o dígito imediatamente anterior
                new_text = current_text[:cursor_pos - 2] + current_text[cursor_pos:]
                self.var.set(new_text)
                self.icursor(cursor_pos - 2)
                self._updating = False
                
                # Recalcula os dígitos internos
                self._digits = "".join(c for c in new_text if c.isdigit())
                return "break"  # Impede o comportamento padrão do backspace

    def _format_date(self, *args):
        """Formata o texto reativamente baseado no buffer de dígitos limpos."""
        if self._updating:
            return
            
        self._updating = True
        try:
            current_text = self.get()
            cursor_pos = self.index(tk.INSERT)
            
            # Conta os dígitos numéricos presentes antes da posição atual do cursor
            digits_before_cursor = sum(1 for c in current_text[:cursor_pos] if c.isdigit())
            
            # Filtra apenas os dígitos e limita a 8
            self._digits = "".join(c for c in current_text if c.isdigit())[:8]
            
            # Gera a formatação derivada (buffer -> máscara)
            formatted = ""
            if len(self._digits) <= 2:
                formatted = self._digits
            elif len(self._digits) <= 4:
                formatted = f"{self._digits[:2]}/{self._digits[2:]}"
            else:
                formatted = f"{self._digits[:2]}/{self._digits[2:4]}/{self._digits[4:]}"
                
            self.var.set(formatted)
            
            # Reposiciona o cursor de forma estável
            new_cursor_pos = 0
            digits_counter = 0
            for char in formatted:
                if digits_counter < digits_before_cursor:
                    if char.isdigit():
                        digits_counter += 1
                    new_cursor_pos += 1
                else:
                    break
                    
            self.icursor(new_cursor_pos)
        finally:
            self._updating = False

    def get_digits(self):
        """Retorna apenas a string de dígitos limpos (ex: '15051985')."""
        return self._digits

    def is_valid_date(self):
        """
        Valida se a data digitada é válida no calendário real (ex: rejeita 31/02/2024).
        Retorna True se estiver vazia (opcional) ou se for uma data lógica real de 8 dígitos.
        """
        text = self.get()
        if not text:
            return True
            
        if len(self._digits) != 8:
            return False
            
        try:
            datetime.strptime(text, "%d/%m/%Y")
            return True
        except ValueError:
            return False

# Exemplo de uso interativo
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Exemplo de Campo de Data com Máscara")
    root.geometry("400x200")
    root.configure(bg="#1E1E2E")
    
    # Estilização básica
    lbl_title = tk.Label(
        root, 
        text="Cadastro de Talento - Entrada de Data", 
        font=("Inter", 12, "bold"), 
        bg="#1E1E2E", 
        fg="#FFFFFF"
    )
    lbl_title.pack(pady=15)
    
    frame = tk.Frame(root, bg="#1E1E2E")
    frame.pack(pady=10)
    
    lbl_data = tk.Label(frame, text="Data de Nascimento (DD/MM/AAAA):", bg="#1E1E2E", fg="#AAB3C5")
    lbl_data.pack(side=tk.LEFT, padx=5)
    
    # Instanciação do widget customizado
    entry_date = DateMaskEntry(
        frame, 
        font=("Inter", 11), 
        bg="#0F0F1A", 
        fg="#FFFFFF", 
        insertbackground="#FFFFFF", # Cursor branco
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground="#313244",
        highlightcolor="#F08A00"
    )
    entry_date.pack(side=tk.LEFT, padx=5)
    entry_date.focus_set()
    
    def verificar_data():
        if entry_date.is_valid_date() and len(entry_date.get_digits()) == 8:
            messagebox.showinfo("Sucesso", f"Data válida cadastrada: {entry_date.get()}")
        elif len(entry_date.get_digits()) == 0:
            messagebox.showwarning("Aviso", "O campo de data está vazio.")
        else:
            messagebox.showerror("Erro", f"A data '{entry_date.get()}' é inválida!")
            
    btn = tk.Button(
        root, 
        text="Validar Data", 
        command=verificar_data,
        bg="#F08A00",
        fg="#000000",
        activebackground="#FF9D1F",
        relief=tk.FLAT,
        font=("Inter", 10, "bold")
    )
    btn.pack(pady=15)
    
    root.mainloop()
