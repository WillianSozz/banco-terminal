# Designed with https://visualtkinter.com - paste this file into File > Import there to edit it visually
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import textwrap
import os

class ToolTip:
    """Small hover tooltip. tkinter has no built-in one."""

    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip = None
        self._job = None
        # add="+" so this never replaces bindings the widget already has.
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._job = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._job is not None:
            self.widget.after_cancel(self._job)
            self._job = None

    def _show(self):
        if self.tip is not None:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        # No title bar or border — it should look like a tooltip, not a window.
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3,
        ).pack()

    def _hide(self, _event=None):
        self._cancel()
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


THEME_BG = "#eef3ec"
THEME_FG = "#1e3a26"
THEME_ACCENT = "#3a7d44"
THEME_ACCENT_FG = "#ffffff"
THEME_FIELD_BG = "#ffffff"
THEME_FONT = ("Verdana", 10)


def apply_theme(root):
    """Apply the project theme as defaults; per-widget options override these."""
    root.configure(bg=THEME_BG)
    root.option_add("*background", THEME_BG)
    root.option_add("*foreground", THEME_FG)
    root.option_add("*font", THEME_FONT)
    root.option_add("*Entry.background", THEME_FIELD_BG)
    root.option_add("*Text.background", THEME_FIELD_BG)
    root.option_add("*Listbox.background", THEME_FIELD_BG)
    root.option_add("*Button.background", THEME_ACCENT)
    root.option_add("*Button.foreground", THEME_ACCENT_FG)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=THEME_BG, foreground=THEME_FG, fieldbackground=THEME_FIELD_BG, font=THEME_FONT)
    
class EXTRATOBANCARIO:
    def __init__(self, master):
        root = tk.Toplevel(master)
        self.root = root
        root.title("EXTRATO BANCARIO")
        root.geometry("600x600")
        apply_theme(root)

        self.b_exportar_pdf = tk.Button(root, text="Exportar PDF", command=self.on_b_exportar_pdf)
        self.b_exportar_pdf.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        self.text_extrato = tk.Text(root)
        self.text_extrato.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=4, pady=4)

        root.columnconfigure(0, minsize=240, weight=1)
        root.columnconfigure(1, minsize=104, weight=1)
        root.columnconfigure(2, minsize=240, weight=1)
        root.rowconfigure(0, minsize=518, weight=1)
        root.rowconfigure(1, minsize=40)

    def on_b_exportar_pdf(self):
        


        # Perguntar onde salvar
        caminho = filedialog.asksaveasfilename(
            parent=self.root,
            title="Salvar extrato em PDF",
            defaultextension=".pdf",
            initialfile="Extrato_Banco_Sozz.pdf",
            filetypes=[
                ("Arquivo PDF", "*.pdf")
            ]
        )

        # Se cancelar, não faz nada
        if not caminho:
            return

        try:
            # Pegar o texto do extrato exibido no Tkinter
            conteudo = self.text_extrato.get("1.0", "end-1c")

            # Configuração de cupom térmico de 80 mm
            largura = 80 * mm
            margem = 5 * mm
            altura_linha = 4 * mm

            # Ajustar as linhas para a largura do cupom
            linhas = []

            for linha in conteudo.splitlines():
                if not linha.strip():
                    linhas.append("")
                else:
                    linhas.extend(
                        textwrap.wrap(
                            linha,
                            width=40,
                            break_long_words=True,
                            break_on_hyphens=False
                        ) or [""]
                    )

            # Altura calculada conforme o tamanho do extrato
            altura = max(
                70 * mm,
                (len(linhas) + 8) * altura_linha + 20 * mm
            )

            pdf = canvas.Canvas(
                caminho,
                pagesize=(largura, altura)
            )

            y = altura - 8 * mm

            # Cabeçalho
            pdf.setFont("Courier-Bold", 12)
            pdf.drawCentredString(
                largura / 2, y, "BANCO SOZZ"
            )

            y -= 6 * mm

            pdf.setFont("Courier", 8)
            pdf.drawCentredString(
                largura / 2, y, "COMPROVANTE BANCARIO"
            )

            y -= 5 * mm

            pdf.drawCentredString(
                largura / 2,
                y,
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )

            y -= 5 * mm

            pdf.drawString(
                margem, y, "-" * 40
            )

            y -= 5 * mm

            # Conteúdo do extrato
            pdf.setFont("Courier", 8)

            for linha in linhas:
                if y < 8 * mm:
                    # Criar outra página se necessário
                    pdf.showPage()
                    y = altura - 8 * mm
                    pdf.setFont("Courier", 8)

                pdf.drawString(
                    margem,
                    y,
                    linha[:42]
                )

                y -= altura_linha

            y -= 2 * mm

            pdf.drawString(
                margem, y, "-" * 40
            )

            y -= 5 * mm

            pdf.setFont("Courier-Bold", 8)
            pdf.drawCentredString(
                largura / 2,
                y,
                "OBRIGADO PELA PREFERENCIA!"
            )

            pdf.save()

            messagebox.showinfo(
                "Sucesso",
                f"PDF salvo com sucesso!\n\n{caminho}",
                parent=self.root
            )

            # Opcional: abrir o PDF depois de salvar
            # os.startfile(caminho)

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar o PDF:\n{erro}",
                parent=self.root
            )



class Application:
    def __init__(self, root):
        self.root = root
        root.title("Banco Terminal")
        root.geometry("1270x800")
        root.update_idletasks()
        self.saldo = 0.0
        self.saldo_total_deposito = 0.0
        self.saldo_total_saque = 0.0
        root.geometry(
            f"+{(root.winfo_screenwidth() - 1270) // 2}"
            f"+{(root.winfo_screenheight() - 800) // 2}"
        )
        apply_theme(root)

        self.optionmenu1_var = tk.StringVar()
        self.optionmenu1_var.set("Depositar")

        self.ttl_banco_terminal = tk.Label(root, text="BANCO TERMINAL", font=("Helvetica", 19, "bold"))
        self.ttl_banco_terminal.grid(row=0, column=1, rowspan=2, columnspan=7, sticky="w", padx=4, pady=4)

        self.separator1 = ttk.Separator(root, orient="horizontal")
        self.separator1.grid(row=1, column=0, rowspan=2, columnspan=9, sticky="ew", padx=4, pady=4)

        self.label2 = tk.Label(root, text="Digite o valor desejado:", font=("Helvetica", 14, "bold"))
        self.label2.grid(row=3, column=1, sticky="w", padx=4, pady=4)

        self.campo_digitar = tk.Entry(root)
        self.campo_digitar.grid(row=3, column=2, columnspan=2, sticky="ew", padx=4, pady=4)

        self.optionmenu1 = tk.OptionMenu(root, self.optionmenu1_var, "Depositar", "Sacar", "Extrato")
        self.optionmenu1.grid(row=3, column=4, sticky="w", padx=4, pady=4)
        ToolTip(self.optionmenu1, "Escolha a operação")

        self.text1 = tk.Text(root)
        self.text1.grid(row=5, column=1, columnspan=7, sticky="nsew", padx=4, pady=4)

        self.b_Executar = tk.Button(root, text="Executar", command=self.on_b_Executar, font=("Helvetica", 10, "bold"))
        self.b_Executar.grid(row=3, column=6, sticky="w", padx=4, pady=4)

        self.label3 = tk.Label(root, text="Seu saldo é de: R$ 0,00", font=("Helvetica", 14, "bold"))
        self.label3.grid(row=4, column=1, columnspan=2, sticky="w", padx=4, pady=4)

        root.columnconfigure(0, minsize=308, weight=1)
        root.columnconfigure(1, minsize=268, weight=1)
        root.columnconfigure(2, minsize=38, weight=1)
        root.columnconfigure(3, minsize=88, weight=1)
        root.columnconfigure(4, minsize=118, weight=1)
        root.columnconfigure(5, minsize=68, weight=1)
        root.columnconfigure(6, minsize=104, weight=1)
        root.columnconfigure(7, minsize=32, weight=1)
        root.columnconfigure(8, minsize=318, weight=1)
        root.rowconfigure(0, minsize=68)
        root.rowconfigure(1, minsize=18)
        root.rowconfigure(2, minsize=18)
        root.rowconfigure(3, minsize=40)
        root.rowconfigure(4, minsize=38)
        root.rowconfigure(5, minsize=518, weight=1)


    def open_extrato_bancario(self):
        return EXTRATOBANCARIO(self.root)


    def on_b_Executar(self):
    

        agora = datetime.now()
        data_hora = agora.strftime("%d/%m/%Y %H:%M:%S")
        
        
        # ===============================================
        # DEPOSITAR
        # ===============================================

        if self.optionmenu1_var.get() == 'Depositar':
            try:
                valor_adicionado = float(self.campo_digitar.get().replace(',', '.'))

                if valor_adicionado <= 0:
                    self.text1.insert(tk.END, f"{data_hora} - Digite um valor maior que zero.\n")
                    return

                self.saldo += valor_adicionado
                
                self.saldo_total_deposito += valor_adicionado

                valor_formatado = f'{valor_adicionado:,.2f}'
                valor_formatado = valor_formatado.replace(',', '.')

                saldo_formatado = f'{self.saldo:,.2f}'
                saldo_formatado = saldo_formatado.replace(',', '.')

                self.text1.insert(
                    '1.0',
                    f'{data_hora} - Depósito: R$ {valor_formatado}\n'
                )

                self.label3.config(
                    text=f'Seu saldo é de: R$ {saldo_formatado}'
                )

                self.campo_digitar.delete(0, tk.END)

            except ValueError:
                self.text1.insert('1.0', f"{data_hora} - Digite um valor numérico válido.\n")
                
        # ===============================================
        # SACAR
        # ===============================================
            
        if self.optionmenu1_var.get() == 'Sacar':
            
            try:
                valor_adicionado = float(self.campo_digitar.get().replace(',', '.'))
            
                if valor_adicionado <= 0:
                                self.text1.insert(tk.END, f"{data_hora} - Digite um valor maior que zero.\n")
                                return
                            
                if self.saldo < valor_adicionado: 
                    self.text1.insert(
                                        '1.0',
                                        f'{data_hora} - Você não possui saldo suficiente, seu saldo é de: R$ {self.saldo:,.2f}\n'
                                    )
                else: 
                    self.saldo -= valor_adicionado
                    
                    self.saldo_total_saque += valor_adicionado
            
                    valor_formatado = f'{valor_adicionado:,.2f}'
                    valor_formatado = valor_formatado.replace(',', '.')
                
                    saldo_formatado = f'{self.saldo:,.2f}'
                    saldo_formatado = saldo_formatado.replace(',', '.')
                
                    self.text1.insert(
                        '1.0',
                        f'{data_hora} - Saque: R$ {valor_formatado}\n'
                    )
                
                    self.label3.config(
                                    text=f'Seu saldo é de: R$ {saldo_formatado}'
                    )
                
                    self.campo_digitar.delete(0, tk.END)
            
            except ValueError:
                self.text1.insert('1.0', f"{data_hora} - Digite um valor numérico válido.\n")

        # ===============================================
        # EXTRATO
        # ===============================================
        
        if self.optionmenu1_var.get() == 'Extrato':

            extrato = EXTRATOBANCARIO(self.root)
            
            movimentacoes = self.text1.get("1.0", tk.END).strip()
            movimentacoes = "\n".join(
                linha
                for linha in movimentacoes.splitlines()
                if "Digite um valor numérico válido." not in linha
                if 'Você não possui saldo suficiente, seu saldo é de: R$' not in linha
            )

            agora = datetime.now()
            data_hora = agora.strftime("%d/%m/%Y às %H:%M:%S")

            texto_extrato = f"""
====================================
BANCO TERMINAL - EXTRATO BANCÁRIO
====================================
Data de emissão: {data_hora}

--------- RESUMO FINANCEIRO --------

Total de depósitos: R$ {self.saldo_total_deposito:,.2f}
Total de saques:    R$ {self.saldo_total_saque:,.2f}

--------- MOVIMENTAÇÕES ---------

{movimentacoes}

-----------------------------------
SALDO ATUAL:        R$ {self.saldo:,.2f}
-----------------------------------

Obrigado por utilizar o Banco Terminal!
===================================
            """
            extrato.text_extrato.insert('1.0', texto_extrato)
            return



if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
