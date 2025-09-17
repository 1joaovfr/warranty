import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
import ttkbootstrap as ttkb
from ttkbootstrap.dialogs import Messagebox
import db_manager 
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class App(ttkb.Window):
    def __init__(self, title="Sistema de Gestão de Garantias", size=(1300, 800)):
        super().__init__(themename="cosmo")
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])

        self.itens_nota = []
        self.codigos_avaria_map = {} 
        self.id_item_selecionado = None

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.tab_lancamento = ttk.Frame(self.notebook, padding=(10))
        self.tab_analise = ttk.Frame(self.notebook, padding=(10))
        self.tab_visualizacao = ttk.Frame(self.notebook, padding=(10))
        self.tab_gestao = ttk.Frame(self.notebook, padding=(10))

        self.notebook.add(self.tab_lancamento, text='  Lançamento de Nota Fiscal  ')
        self.notebook.add(self.tab_analise, text='  Análise de Garantia  ')
        self.notebook.add(self.tab_visualizacao, text='  Visualizar Garantias  ')
        self.notebook.add(self.tab_gestao, text='  Gestão de Dados  ')
        
        self._criar_widgets_lancamento(self.tab_lancamento)
        self._criar_widgets_analise(self.tab_analise)
        self._criar_widgets_visualizacao(self.tab_visualizacao)
        self._criar_widgets_gestao(self.tab_gestao)
        
        self._carregar_dados_iniciais()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        plt.close('all')
        self.destroy()

    # =================================================================================
    # --- ABAS 1, 2 e 3 (Omitidas para brevidade) ---
    # =================================================================================
    # main.py

    def _criar_widgets_lancamento(self, parent_tab):
        main_frame = ttk.Frame(parent_tab)
        main_frame.pack(fill=BOTH, expand=YES)
        titulo_label = ttk.Label(main_frame, text="Lançamento de Nota Fiscal", font=("Helvetica", 16, "bold"))
        titulo_label.pack(pady=(0, 20), anchor="w")
        dados_nota_frame = ttk.LabelFrame(main_frame, text="Dados do Cliente e Nota Fiscal", padding=15)
        dados_nota_frame.pack(fill=X, pady=(0, 10))
        dados_nota_frame.columnconfigure((1, 3), weight=1)
        ttk.Label(dados_nota_frame, text="Empresa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.empresa_combo = ttk.Combobox(dados_nota_frame, state="readonly")
        self.empresa_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(dados_nota_frame, text="CNPJ:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cnpj_entry = ttk.Entry(dados_nota_frame)
        self.cnpj_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.cnpj_entry.bind("<FocusOut>", self.buscar_cliente_por_cnpj)
        ttk.Label(dados_nota_frame, text="Nome Cliente:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.razao_social_entry = ttk.Entry(dados_nota_frame, state="readonly")
        self.razao_social_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Label(dados_nota_frame, text="Nº da Nota:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        self.num_nota_entry = ttk.Entry(dados_nota_frame)
        self.num_nota_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(dados_nota_frame, text="Data da Nota:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
        self.data_nota_entry = ttkb.DateEntry(dados_nota_frame, bootstyle="primary", dateformat="%d/%m/%Y")
        self.data_nota_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # --- ALTERAÇÃO APLICADA AQUI ---
        # Em vez de substituir o comando, nós "escutamos" o clique do mouse
        # para então chamar a função de posicionar o popup.
        self.data_nota_entry.button.bind("<Button-1>", lambda event: self.after(10, lambda: self._posicionar_popup(self.data_nota_entry)))

        add_item_frame = ttk.LabelFrame(main_frame, text="Adicionar Itens à Nota", padding=15)
        add_item_frame.pack(fill=X, pady=10)
        ttk.Label(add_item_frame, text="Cód. Item:").pack(side=LEFT, padx=(0, 5))
        self.item_entry = ttk.Entry(add_item_frame, width=15)
        self.item_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Label(add_item_frame, text="Quantidade:").pack(side=LEFT, padx=(15, 5))
        self.qtd_entry = ttk.Entry(add_item_frame, width=8)
        self.qtd_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Label(add_item_frame, text="Valor Unitário:").pack(side=LEFT, padx=(15, 5))
        self.valor_entry = ttk.Entry(add_item_frame, width=10)
        self.valor_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        self.ressarc_check_var = tk.BooleanVar()
        self.ressarc_check = ttk.Checkbutton(add_item_frame, text="Ressarcimento?", variable=self.ressarc_check_var, command=self._toggle_ressarcimento_entry, bootstyle="primary")
        self.ressarc_check.pack(side=LEFT, padx=(20, 5))
        self.ressarc_label = ttk.Label(add_item_frame, text="Valor Ressarc:")
        self.ressarc_entry = ttk.Entry(add_item_frame, width=10)
        self.add_item_button = ttk.Button(add_item_frame, text="Adicionar Item", command=self.adicionar_item_lista, bootstyle="success")
        self.add_item_button.pack(side=RIGHT, padx=(20, 0))
        lista_itens_frame = ttk.LabelFrame(main_frame, text="Itens da Nota", padding=15)
        lista_itens_frame.pack(fill=BOTH, expand=YES, pady=10)
        colunas = ("codigo", "quantidade", "valor_unit", "ressarcimento")
        self.tree_lancamento = ttk.Treeview(lista_itens_frame, columns=colunas, show="headings")
        self.tree_lancamento.heading("codigo", text="Código do Item")
        self.tree_lancamento.heading("quantidade", text="Quantidade")
        self.tree_lancamento.heading("valor_unit", text="Valor Unitário")
        self.tree_lancamento.heading("ressarcimento", text="Ressarcimento")
        self.tree_lancamento.column("codigo", anchor=CENTER, width=120)
        self.tree_lancamento.column("quantidade", anchor=CENTER, width=80)
        self.tree_lancamento.column("valor_unit", anchor=CENTER, width=100)
        self.tree_lancamento.column("ressarcimento", anchor=CENTER, width=100)
        self.tree_lancamento.pack(side=LEFT, fill=BOTH, expand=YES)
        acoes_frame = ttk.Frame(main_frame)
        acoes_frame.pack(fill=X, pady=(10, 0))
        self.save_button = ttk.Button(acoes_frame, text="Guardar Nota Fiscal", command=self.salvar_nota_fiscal, bootstyle="primary")
        self.save_button.pack(side=RIGHT, padx=5)
        self.clear_button = ttk.Button(acoes_frame, text="Limpar Campos", command=self.limpar_tela_lancamento, bootstyle="secondary-outline")
        self.clear_button.pack(side=RIGHT, padx=5)
    
    def buscar_cliente_por_cnpj(self, event=None):
        cnpj = self.cnpj_entry.get().strip()
        if not cnpj: return
        cliente_data = db_manager.buscar_cliente_por_cnpj(cnpj)
        nome_cliente = cliente_data['nome_cliente'] if cliente_data else "CNPJ não encontrado!"
        self.razao_social_entry.config(state="normal")
        self.razao_social_entry.delete(0, END)
        self.razao_social_entry.insert(0, nome_cliente)
        self.razao_social_entry.config(state="readonly")

    def adicionar_item_lista(self):
        codigo = self.item_entry.get().strip()
        qtd_str = self.qtd_entry.get().strip()
        valor_str = self.valor_entry.get().strip().replace(',', '.')
        
        if not all([codigo, qtd_str, valor_str]):
            Messagebox.show_error("Preencha todos os campos do item.", "Erro de Validação")
            return
        if not db_manager.buscar_produto_por_codigo(codigo):
            Messagebox.show_error(f"O código de item '{codigo}' não foi encontrado.", "Item Inválido")
            return
        try:
            qtd = int(qtd_str)
            valor = float(valor_str)
            
            # --- LÓGICA DO RESSARCIMENTO ---
            ressarcimento = 0.0
            ressarcimento_str = "-"
            if self.ressarc_check_var.get():
                ressarc_val_str = self.ressarc_entry.get().strip().replace(',', '.')
                if not ressarc_val_str:
                    Messagebox.show_error("O valor de ressarcimento deve ser preenchido.", "Erro de Validação")
                    return
                ressarcimento = float(ressarc_val_str)
                ressarcimento_str = f"R$ {ressarcimento:.2f}"
            # --- FIM DA LÓGICA ---

        except ValueError:
            Messagebox.show_error("Quantidade e Valores devem ser números.", "Erro de Validação")
            return
            
        valor_unit_str = f"R$ {valor:.2f}"
        self.tree_lancamento.insert("", END, values=(codigo, f"{qtd}", valor_unit_str, ressarcimento_str))
        self.itens_nota.append({"codigo": codigo, "quantidade": qtd, "valor": valor, "ressarcimento": ressarcimento if self.ressarc_check_var.get() else None})
        
        # Limpar campos
        self.item_entry.delete(0, END)
        self.qtd_entry.delete(0, END)
        self.valor_entry.delete(0, END)
        self.ressarc_entry.delete(0, END)
        self.ressarc_check_var.set(False)
        self._toggle_ressarcimento_entry()
        self.item_entry.focus()

    def _toggle_ressarcimento_entry(self):
        if self.ressarc_check_var.get():
            self.ressarc_label.pack(side=LEFT, padx=(15, 5))
            self.ressarc_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        else:
            self.ressarc_label.pack_forget()
            self.ressarc_entry.pack_forget()
            self.ressarc_entry.delete(0, END)

    def salvar_nota_fiscal(self):
        cnpj = self.cnpj_entry.get().strip()
        if not db_manager.buscar_cliente_por_cnpj(cnpj):
            Messagebox.show_error("CNPJ inválido ou não registado.", "Erro de Validação"); return
        if not self.num_nota_entry.get().strip():
            Messagebox.show_error("O campo 'Nº da Nota' é obrigatório.", "Erro de Validação"); return
        if not self.itens_nota:
            Messagebox.show_error("Adicione pelo menos um item à nota.", "Erro de Validação"); return
        numero_nota = self.num_nota_entry.get().strip()
        data_nota = self.data_nota_entry.get_date().strftime('%Y-%m-%d')
        sucesso, mensagem = db_manager.salvar_nota_e_itens(cnpj, numero_nota, data_nota, self.itens_nota)
        if sucesso:
            Messagebox.show_info(mensagem, "Sucesso")
            self.limpar_tela_lancamento()
            self.carregar_itens_pendentes()
            self.aplicar_filtros()
            self._atualizar_aba_gestao()
        else: Messagebox.show_error(mensagem, "Erro ao Guardar")



    def limpar_tela_lancamento(self):
        self.empresa_combo.set(''); self.cnpj_entry.delete(0, END); self.num_nota_entry.delete(0, END)
        self.razao_social_entry.config(state="normal"); self.razao_social_entry.delete(0, END); self.razao_social_entry.config(state="readonly")
        for i in self.tree_lancamento.get_children(): self.tree_lancamento.delete(i)
        self.itens_nota.clear()
        
        # Limpar e resetar campos de ressarcimento
        self.ressarc_entry.delete(0, END)
        self.ressarc_check_var.set(False)
        self._toggle_ressarcimento_entry()

        self.cnpj_entry.focus()


        
    def _posicionar_popup(self, date_entry_widget):
        try:
            calendario_popup = date_entry_widget.calendar
            widget_x = date_entry_widget.winfo_rootx()
            widget_y = date_entry_widget.winfo_rooty()
            widget_altura = date_entry_widget.winfo_height()
            nova_pos_x = widget_x
            nova_pos_y = widget_y + widget_altura + 5
            calendario_popup.geometry(f'+{nova_pos_x}+{nova_pos_y}')
        except (AttributeError, tk.TclError):
            pass

# main.py

    def _criar_widgets_analise(self, parent_tab):
        lista_frame = ttk.LabelFrame(parent_tab, text="Itens Pendentes de Análise", padding=15)
        lista_frame.pack(fill=X, pady=(0, 10))
        # Adicionada a coluna 'ressarcimento'
        cols = ("id", "analise", "nota", "cliente", "produto", "data", "ressarcimento")
        self.tree_analise = ttk.Treeview(lista_frame, columns=cols, show="headings", height=12)
        self.tree_analise.heading("id", text="ID")
        self.tree_analise.heading("analise", text="Cód. Análise")
        self.tree_analise.heading("nota", text="Nº Nota")
        self.tree_analise.heading("cliente", text="Cliente")
        self.tree_analise.heading("produto", text="Cód. Produto")
        self.tree_analise.heading("data", text="Data Nota")
        self.tree_analise.heading("ressarcimento", text="Ressarcimento") # Novo heading
        
        self.tree_analise.column("id", width=50, anchor=CENTER)
        self.tree_analise.column("analise", width=100, anchor=CENTER)
        self.tree_analise.column("nota", width=80, anchor=CENTER)
        self.tree_analise.column("cliente", width=250, anchor=CENTER)
        self.tree_analise.column("produto", width=120, anchor=CENTER)
        self.tree_analise.column("data", width=100, anchor=CENTER)
        self.tree_analise.column("ressarcimento", width=100, anchor=CENTER) # Novas propriedades da coluna

        v_scroll = ttk.Scrollbar(lista_frame, orient=VERTICAL, command=self.tree_analise.yview)
        self.tree_analise.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side=RIGHT, fill=Y)
        self.tree_analise.pack(side=LEFT, fill=BOTH, expand=YES)
        self.tree_analise.bind("<<TreeviewSelect>>", self.on_item_analise_select)
        self.form_analise_frame = ttk.LabelFrame(parent_tab, text="Formulário de Análise", padding=15)
        self.form_analise_frame.pack(fill=BOTH, expand=YES)
        self.form_analise_frame.columnconfigure(1, weight=1); self.form_analise_frame.columnconfigure(3, weight=1)
        ttk.Label(self.form_analise_frame, text="Cód. Análise:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.analise_cod_entry = ttk.Entry(self.form_analise_frame, state="readonly")
        self.analise_cod_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.form_analise_frame, text="Nº de Série:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.analise_serie_entry = ttk.Entry(self.form_analise_frame)
        self.analise_serie_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(self.form_analise_frame, text="Cód. Avaria:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.analise_avaria_combo = ttk.Combobox(self.form_analise_frame, state="readonly")
        self.analise_avaria_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.analise_avaria_combo.bind("<<ComboboxSelected>>", self.atualizar_status_procedencia)
        self.analise_status_label = ttk.Label(self.form_analise_frame, text="Status: -", font=("Helvetica", 10, "bold"))
        self.analise_status_label.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        ttk.Label(self.form_analise_frame, text="Descrição Avaria:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.analise_desc_avaria_entry = ttk.Entry(self.form_analise_frame, state="readonly")
        self.analise_desc_avaria_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Label(self.form_analise_frame, text="Origem:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.analise_origem_combo = ttk.Combobox(self.form_analise_frame, state="readonly", values=["Produzido", "Revenda"])
        self.analise_origem_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.form_analise_frame, text="Fornecedor:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.analise_fornecedor_entry = ttk.Entry(self.form_analise_frame)
        self.analise_fornecedor_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")
        self.save_analise_button = ttk.Button(self.form_analise_frame, text="Guardar Análise", command=self.salvar_analise, bootstyle="primary")
        self.save_analise_button.grid(row=4, column=3, padx=5, pady=20, sticky="e")
        self.set_form_analise_state("disabled")


    def carregar_itens_pendentes(self):
        for i in self.tree_analise.get_children(): self.tree_analise.delete(i)
        itens = db_manager.buscar_itens_pendentes()
        for item in itens:
            data_formatada = datetime.strptime(item['data_nota'], '%Y-%m-%d').strftime('%d/%m/%Y')
            
            # --- ALTERAÇÃO APLICADA AQUI ---
            # Pega o valor do ressarcimento (que é uma string ou None)
            valor_ressarcimento = item['ressarcimento']
            ressarcimento_str = "-" # Valor padrão para exibição

            # Se o valor não for nulo ou vazio, tenta convertê-lo para float
            if valor_ressarcimento:
                try:
                    # Converte a string para float antes de formatar
                    valor_float = float(valor_ressarcimento)
                    ressarcimento_str = f"R$ {valor_float:.2f}"
                except (ValueError, TypeError):
                    # Se a conversão falhar, mantém o valor padrão "-"
                    pass
            
            # Adiciona o valor formatado ao inserir na tabela
            self.tree_analise.insert("", END, values=(
                item['id'], 
                item['codigo_analise'], 
                item['numero_nota'], 
                item['nome_cliente'], 
                item['codigo_produto'], 
                data_formatada,
                ressarcimento_str
            ))

    def on_item_analise_select(self, event=None):
        selecionado = self.tree_analise.focus()
        if not selecionado: return
        self.limpar_form_analise()
        item_values = self.tree_analise.item(selecionado, "values")
        self.id_item_selecionado = item_values[0]
        codigo_analise_selecionado = item_values[1]
        self.analise_cod_entry.config(state="normal")
        self.analise_cod_entry.delete(0, END)
        self.analise_cod_entry.insert(0, codigo_analise_selecionado)
        self.analise_cod_entry.config(state="readonly")
        self.form_analise_frame.config(text=f"Formulário de Análise - Item ID: {self.id_item_selecionado}")
        self.set_form_analise_state("normal")

    def atualizar_status_procedencia(self, event=None):
        cod_avaria = self.analise_avaria_combo.get()
        if not cod_avaria: return
        info_avaria = self.codigos_avaria_map.get(cod_avaria, {})
        classificacao = info_avaria.get('classificacao', '-')
        self.analise_desc_avaria_entry.config(state="normal")
        self.analise_desc_avaria_entry.delete(0, END)
        self.analise_desc_avaria_entry.insert(0, info_avaria.get('descricao', ''))
        self.analise_desc_avaria_entry.config(state="readonly")
        self.analise_status_label.config(text=f"Status: {classificacao}")
        if classificacao == "Procedente": self.analise_status_label.config(bootstyle="success")
        elif classificacao == "Improcedente": self.analise_status_label.config(bootstyle="danger")
        else: self.analise_status_label.config(bootstyle="default")


    def salvar_analise(self):
        if not self.id_item_selecionado: return
        cod_avaria_selecionado = self.analise_avaria_combo.get()
        if not cod_avaria_selecionado:
            Messagebox.show_error("Selecione um código de avaria.", "Erro de Validação")
            return
        
        # O campo 'ressarcimento' foi removido do dicionário de dados
        dados = {
            'codigo_analise': self.analise_cod_entry.get(), 
            'numero_serie': self.analise_serie_entry.get(), 
            'codigo_avaria': cod_avaria_selecionado, 
            'descricao_avaria': self.analise_desc_avaria_entry.get(), 
            'procedente_improcedente': self.codigos_avaria_map.get(cod_avaria_selecionado, {}).get('classificacao'), 
            'produzido_revenda': self.analise_origem_combo.get(), 
            'fornecedor': self.analise_fornecedor_entry.get()
        }
        
        sucesso, msg = db_manager.salvar_analise_item(self.id_item_selecionado, dados)
        if sucesso:
            Messagebox.show_info(msg, "Sucesso")
            self.limpar_form_analise()
            self.carregar_itens_pendentes()
            self.aplicar_filtros()
            self._atualizar_aba_gestao()
        else:
            Messagebox.show_error(msg, "Erro")

    def set_form_analise_state(self, state):
        for widget in self.form_analise_frame.winfo_children():
            try:
                if widget in (self.analise_desc_avaria_entry, self.analise_cod_entry):
                    widget.config(state="readonly" if state == "normal" else "disabled")
                else:
                    widget.config(state=state)
            except tk.TclError:
                pass

    def limpar_form_analise(self):
        self.id_item_selecionado = None
        self.form_analise_frame.config(text="Formulário de Análise")
        self.analise_cod_entry.config(state="normal")
        self.analise_cod_entry.delete(0, END)
        self.analise_cod_entry.config(state="readonly")
        entries = [self.analise_serie_entry, self.analise_fornecedor_entry]
        for entry in entries: entry.delete(0, END)
        self.analise_desc_avaria_entry.config(state="normal")
        self.analise_desc_avaria_entry.delete(0, END)
        self.analise_desc_avaria_entry.config(state="readonly")
        for combo in [self.analise_avaria_combo, self.analise_origem_combo]: combo.set('')
        self.analise_status_label.config(text="Status: -", bootstyle="default")
        self.set_form_analise_state("disabled")

    def _criar_widgets_visualizacao(self, parent_tab):
        filtros_frame = ttk.LabelFrame(parent_tab, text="Filtros de Pesquisa", padding=15)
        filtros_frame.pack(fill=X, pady=(0, 10))
        filtros_frame.columnconfigure((1, 3), weight=1)
        ttk.Label(filtros_frame, text="CNPJ:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filtro_cnpj = ttk.Entry(filtros_frame)
        self.filtro_cnpj.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(filtros_frame, text="Nome Cliente:").grid(row=0, column=2, padx=(15, 5), pady=5, sticky="w")
        self.filtro_razao = ttk.Entry(filtros_frame)
        self.filtro_razao.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(filtros_frame, text="Nº Nota:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.filtro_nota = ttk.Entry(filtros_frame)
        self.filtro_nota.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(filtros_frame, text="Status:").grid(row=1, column=2, padx=(15, 5), pady=5, sticky="w")
        self.filtro_status = ttk.Combobox(filtros_frame, state="readonly", values=["Todos", "Pendente de Análise", "Analisado"])
        self.filtro_status.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self.filtro_status.set("Todos")
        btn_frame = ttk.Frame(filtros_frame)
        btn_frame.grid(row=0, column=4, rowspan=2, columnspan=2, padx=(20, 5), sticky="e")
        self.btn_filtrar = ttk.Button(btn_frame, text="Filtrar", command=self.aplicar_filtros, bootstyle="primary")
        self.btn_filtrar.pack(fill=X, pady=2, ipady=4)
        self.btn_limpar_filtros = ttk.Button(btn_frame, text="Limpar", command=self.limpar_filtros, bootstyle="secondary")
        self.btn_limpar_filtros.pack(fill=X, pady=2, ipady=4)
        lista_geral_frame = ttk.LabelFrame(parent_tab, text="Registos de Garantia", padding=15)
        lista_geral_frame.pack(fill=BOTH, expand=YES)
        cols = ("id", "nota", "data", "cnpj", "cliente", "analise", "produto", "valor", "status", "procedencia")
        self.tree_visualizacao = ttk.Treeview(lista_geral_frame, columns=cols, show="headings", selectmode="extended")
        headings = { "id": ("ID", 40), "nota": ("Nº Nota", 80), "data": ("Data", 80), "cnpj": ("CNPJ", 110), "cliente": ("Cliente", 180), "analise": ("Cód. Análise", 100), "produto": ("Cód. Produto", 100), "valor": ("Valor", 80), "status": ("Status", 120), "procedencia": ("Procedência", 100)}
        for col, (text, width) in headings.items():
            self.tree_visualizacao.heading(col, text=text)
            self.tree_visualizacao.column(col, width=width, anchor=CENTER)
        v_scroll = ttk.Scrollbar(lista_geral_frame, orient=VERTICAL, command=self.tree_visualizacao.yview)
        h_scroll = ttk.Scrollbar(lista_geral_frame, orient=HORIZONTAL, command=self.tree_visualizacao.xview)
        self.tree_visualizacao.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll.pack(side=BOTTOM, fill=X)
        self.tree_visualizacao.pack(fill=BOTH, expand=YES)
        acoes_vis_frame = ttk.Frame(parent_tab)
        acoes_vis_frame.pack(fill=X, pady=(10, 0))
        self.btn_excluir = ttk.Button(acoes_vis_frame, text="Excluir Selecionado(s)", command=self.excluir_item_selecionado, bootstyle="danger")
        self.btn_excluir.pack(side=RIGHT, padx=5)
        self.btn_editar = ttk.Button(acoes_vis_frame, text="Editar Selecionado", command=self.editar_item_selecionado, bootstyle="info")
        self.btn_editar.pack(side=RIGHT, padx=5)

    def aplicar_filtros(self):
        filtros = { 'cnpj': self.filtro_cnpj.get().strip(), 'razao_social': self.filtro_razao.get().strip(), 'numero_nota': self.filtro_nota.get().strip(), 'status': self.filtro_status.get() }
        for i in self.tree_visualizacao.get_children(): self.tree_visualizacao.delete(i)
        resultados = db_manager.buscar_garantias_filtradas(filtros)
        for item in resultados:
            data_formatada = datetime.strptime(item['data_nota'], '%Y-%m-%d').strftime('%d/%m/%Y')
            codigo_analise = item['codigo_analise'] or '-'
            procedencia = item['procedente_improcedente'] or '-'
            valor_str = f"R$ {item['valor_item']:.2f}" if item['valor_item'] is not None else '-'
            self.tree_visualizacao.insert("", END, values=(item['id'], item['numero_nota'], data_formatada, item['cnpj'], item['nome_cliente'], codigo_analise, item['codigo_produto'], valor_str, item['status'], procedencia))
            
    def limpar_filtros(self):
        self.filtro_cnpj.delete(0, END); self.filtro_razao.delete(0, END); self.filtro_nota.delete(0, END); self.filtro_status.set("Todos"); self.aplicar_filtros()

    def excluir_item_selecionado(self):
        selecionados = self.tree_visualizacao.selection()
        if not selecionados:
            Messagebox.show_warning("Nenhum item selecionado.", "Aviso")
            return
        ids_para_excluir = [self.tree_visualizacao.item(item, "values")[0] for item in selecionados]
        quantidade = len(ids_para_excluir)
        singular_plural = "item" if quantidade == 1 else "itens"
        confirmacao = Messagebox.yesno(f"Tem a certeza de que quer excluir os {quantidade} {singular_plural} selecionado(s)?", "Confirmação de Exclusão")
        if confirmacao == "Yes":
            sucesso, msg = db_manager.excluir_varios_itens(ids_para_excluir)
            if sucesso:
                Messagebox.show_info(msg, "Sucesso")
                self.aplicar_filtros()
                self.carregar_itens_pendentes()
                self._atualizar_aba_gestao()
            else:
                Messagebox.show_error(msg, "Erro")
    def editar_item_selecionado(self):
        selecionados = self.tree_visualizacao.selection()
        if not selecionados:
            Messagebox.show_warning("Nenhum item selecionado para editar.", "Aviso")
            return
        if len(selecionados) > 1:
            Messagebox.show_info("Por favor, selecione apenas um item para editar.", "Aviso")
            return
        item_id_interno = selecionados[0]
        item_values = self.tree_visualizacao.item(item_id_interno, "values")
        if item_values[8] == 'Pendente de Análise':
            Messagebox.show_warning("Não é possível editar um item que ainda não foi analisado.", "Ação Inválida")
            return
        EditorWindow(self, item_values[0], self.codigos_avaria_map)

    # =================================================================================
    # --- ABA 4: GESTÃO DE DADOS ---
    # =================================================================================
    def _criar_widgets_gestao(self, parent_tab):
        # Frame para os botões de navegação da aba
        control_frame = ttk.Frame(parent_tab)
        control_frame.pack(fill=X, pady=(0, 5))
        self.btn_ver_tabela = ttk.Button(control_frame, text="Visualizar Tabela", command=self._mostrar_view_tabela)
        self.btn_ver_tabela.pack(side=LEFT, padx=5)
        self.btn_ver_dashboard = ttk.Button(control_frame, text="Visualizar Dashboard", command=self._mostrar_view_dashboard)
        self.btn_ver_dashboard.pack(side=LEFT, padx=5)
        self.btn_ver_ressarcimento = ttk.Button(control_frame, text="Visualizar Ressarcimentos", command=self._mostrar_view_ressarcimento)
        self.btn_ver_ressarcimento.pack(side=LEFT, padx=5)

        # Frame para os filtros, que agora são aplicados a todas as visualizações
        filtros_gestao_frame = ttk.LabelFrame(parent_tab, text="Filtros", padding=10)
        filtros_gestao_frame.pack(fill=X, pady=5)
        
        ttk.Label(filtros_gestao_frame, text="Ano:").pack(side=LEFT, padx=(5, 2))
        self.combo_ano_gestao = ttk.Combobox(filtros_gestao_frame, state="readonly", width=10)
        self.combo_ano_gestao.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(filtros_gestao_frame, text="Mês:").pack(side=LEFT, padx=(5, 2))
        meses = ["Todos", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.combo_mes_gestao = ttk.Combobox(filtros_gestao_frame, state="readonly", values=meses, width=15)
        self.combo_mes_gestao.pack(side=LEFT, padx=(0, 10))

        ttk.Label(filtros_gestao_frame, text="Cliente:").pack(side=LEFT, padx=(5, 2))
        self.combo_cliente_gestao = ttk.Combobox(filtros_gestao_frame, state="readonly", width=25)
        self.combo_cliente_gestao.pack(side=LEFT, padx=(0, 10))

        ttk.Label(filtros_gestao_frame, text="Cód. Produto:").pack(side=LEFT, padx=(5, 2))
        self.combo_produto_gestao = ttk.Combobox(filtros_gestao_frame, state="readonly", width=20)
        self.combo_produto_gestao.pack(side=LEFT, padx=(0, 10))
        
        btn_limpar = ttk.Button(filtros_gestao_frame, text="Limpar Filtros", command=self._on_filtro_gestao_limpar, bootstyle="secondary")
        btn_limpar.pack(side=RIGHT, padx=5)
        btn_filtrar = ttk.Button(filtros_gestao_frame, text="Filtrar", command=self._on_filtro_gestao_aplicar, bootstyle="primary")
        btn_filtrar.pack(side=RIGHT, padx=5)

        # Container para as diferentes visualizações
        self.container_gestao = ttk.Frame(parent_tab)
        self.container_gestao.pack(fill=BOTH, expand=YES)
        self.frame_tabela_gestao = ttk.Frame(self.container_gestao)
        self._criar_tabela_gestao(self.frame_tabela_gestao)
        self.frame_dashboard_geral_gestao = ttk.Frame(self.container_gestao)
        self._criar_dashboard_geral(self.frame_dashboard_geral_gestao)
        self.frame_dashboard_ressarcimento_gestao = ttk.Frame(self.container_gestao)
        self._criar_dashboard_ressarcimento(self.frame_dashboard_ressarcimento_gestao)
        self._mostrar_view_tabela()

    def _criar_tabela_gestao(self, parent_frame):
        cols = ('id', 'data_lanc', 'num_nota', 'data_nota', 'cnpj', 'cliente', 'grupo_cliente', 
                'cod_analise', 'cod_produto', 'grupo_estoque', 'cod_avaria', 'valor', 'status', 'procedencia', 'ressarcimento')
        self.tree_gestao = ttk.Treeview(parent_frame, columns=cols, show='headings')
        
        headings = {
            'id': ('ID', 40), 'data_lanc': ('Data Lanç', 90), 'num_nota': ('Nº Nota', 80),
            'data_nota': ('Data Nota', 90), 'cnpj': ('CNPJ', 110), 'cliente': ('Cliente', 150),
            'grupo_cliente': ('Grupo Cliente', 100), 'cod_analise': ('Cód. Análise', 90),
            'cod_produto': ('Cód. Produto', 90), 'grupo_estoque': ('Grupo Estoque', 100),
            'cod_avaria': ('Cód. Avaria', 80), 'valor': ('Valor', 80), 'status': ('Status', 110),
            'procedencia': ('Procedência', 100), 'ressarcimento': ('Ressarcimento', 100)
        }
        for col, (text, width) in headings.items():
            self.tree_gestao.heading(col, text=text)
            self.tree_gestao.column(col, width=width, anchor=CENTER)
        
        v_scroll = ttk.Scrollbar(parent_frame, orient=VERTICAL, command=self.tree_gestao.yview)
        h_scroll = ttk.Scrollbar(parent_frame, orient=HORIZONTAL, command=self.tree_gestao.xview)
        self.tree_gestao.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll.pack(side=BOTTOM, fill=X)
        self.tree_gestao.pack(fill=BOTH, expand=YES)

# main.py

    def _criar_dashboard_geral(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1) 
        parent_frame.columnconfigure(1, weight=0)
        parent_frame.rowconfigure(0, weight=1)

        self.frame_grafico_geral_canvas = ttk.LabelFrame(parent_frame, text="Distribuição de Status (Geral)", padding=15)
        self.frame_grafico_geral_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # --- ALTERAÇÕES AQUI ---
        # 1. Definida uma largura fixa de 350 pixels
        stats_frame = ttk.LabelFrame(parent_frame, text="Resumo de Valores e Quantidades (Geral)", padding=15, width=350)
        stats_frame.grid(row=0, column=1, sticky="ns")
        # 2. Impede que os widgets internos alterem o tamanho do frame
        stats_frame.pack_propagate(False)
        
        # O conteúdo do stats_frame continua o mesmo
        ttk.Label(stats_frame, text="Procedentes", font=("Helvetica", 12, "bold"), foreground="#28a745").pack(anchor='w', pady=(0, 5))
        self.label_procedente_qtd = ttk.Label(stats_frame, text="Quantidade: -")
        self.label_procedente_qtd.pack(anchor='w', padx=10)
        self.label_procedente_valor = ttk.Label(stats_frame, text="Valor Total: R$ -")
        self.label_procedente_valor.pack(anchor='w', padx=10, pady=(0, 15))
        ttk.Label(stats_frame, text="Improcedentes", font=("Helvetica", 12, "bold"), foreground="#dc3545").pack(anchor='w', pady=(0, 5))
        self.label_improcedente_qtd = ttk.Label(stats_frame, text="Quantidade: -")
        self.label_improcedente_qtd.pack(anchor='w', padx=10)
        self.label_improcedente_valor = ttk.Label(stats_frame, text="Valor Total: R$ -")
        self.label_improcedente_valor.pack(anchor='w', padx=10, pady=(0, 15))
        ttk.Label(stats_frame, text="Pendentes de Análise", font=("Helvetica", 12, "bold"), foreground="#6c757d").pack(anchor='w', pady=(0, 5))
        self.label_pendente_qtd = ttk.Label(stats_frame, text="Quantidade: -")
        self.label_pendente_qtd.pack(anchor='w', padx=10)
        self.label_pendente_valor = ttk.Label(stats_frame, text="Valor Total: R$ -")
        self.label_pendente_valor.pack(anchor='w', padx=10, pady=(0, 15))
        ttk.Separator(stats_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        ttk.Label(stats_frame, text="Total Recebido", font=("Helvetica", 12, "bold"), foreground="#17a2b8").pack(anchor='w', pady=(0, 5))
        self.label_total_qtd = ttk.Label(stats_frame, text="Quantidade Total: -")
        self.label_total_qtd.pack(anchor='w', padx=10)
        self.label_total_valor = ttk.Label(stats_frame, text="Valor Total: R$ -")
        self.label_total_valor.pack(anchor='w', padx=10)

    # main.py

    def _criar_dashboard_ressarcimento(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=0)
        parent_frame.rowconfigure(0, weight=1)

        self.frame_grafico_ressarcimento_canvas = ttk.LabelFrame(parent_frame, text="Distribuição de Ressarcimentos por Valor", padding=15)
        self.frame_grafico_ressarcimento_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # --- ALTERAÇÕES AQUI ---
        # 1. Definida a MESMA largura fixa de 350 pixels
        stats_frame = ttk.LabelFrame(parent_frame, text="Resumo de Valores de Ressarcimento", padding=15, width=350)
        stats_frame.grid(row=0, column=1, sticky="ns")
        # 2. Impede que os widgets internos alterem o tamanho do frame
        stats_frame.pack_propagate(False)

        # O conteúdo do stats_frame continua o mesmo
        ttk.Label(stats_frame, text="Procedentes", font=("Helvetica", 12, "bold"), foreground="#28a745").pack(anchor='w', pady=(0, 5))
        self.label_ressarc_proc_qtd = ttk.Label(stats_frame, text="Quantidade: -")
        self.label_ressarc_proc_qtd.pack(anchor='w', padx=10)
        self.label_ressarc_proc_valor = ttk.Label(stats_frame, text="Valor Total: R$ -")
        self.label_ressarc_proc_valor.pack(anchor='w', padx=10, pady=(0, 15))
        ttk.Label(stats_frame, text="Improcedentes", font=("Helvetica", 12, "bold"), foreground="#dc3545").pack(anchor='w', pady=(0, 5))
        self.label_ressarc_improc_qtd = ttk.Label(stats_frame, text="Quantidade: -")
        self.label_ressarc_improc_qtd.pack(anchor='w', padx=10)
        self.label_ressarc_improc_valor = ttk.Label(stats_frame, text="Valor Total: R$ -")
        self.label_ressarc_improc_valor.pack(anchor='w', padx=10, pady=(0, 15))
        ttk.Label(stats_frame, text="Pendentes de Análise", font=("Helvetica", 12, "bold"), foreground="#6c757d").pack(anchor='w', pady=(0, 5))
        self.label_ressarc_pend_qtd = ttk.Label(stats_frame, text="Quantidade: -")
        self.label_ressarc_pend_qtd.pack(anchor='w', padx=10)
        self.label_ressarc_pend_valor = ttk.Label(stats_frame, text="Valor Potencial: R$ -")
        self.label_ressarc_pend_valor.pack(anchor='w', padx=10, pady=(0, 15))
        ttk.Separator(stats_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        ttk.Label(stats_frame, text="Total Recebido", font=("Helvetica", 12, "bold"), foreground="#17a2b8").pack(anchor='w', pady=(0, 5))
        self.label_total_ressarc_qtd = ttk.Label(stats_frame, text="Quantidade Total: -")
        self.label_total_ressarc_qtd.pack(anchor='w', padx=10)
        self.label_total_ressarc_valor = ttk.Label(stats_frame, text="Valor Total: R$ -")
        self.label_total_ressarc_valor.pack(anchor='w', padx=10)

    def _mostrar_view_tabela(self):
        self.frame_dashboard_geral_gestao.pack_forget()
        self.frame_dashboard_ressarcimento_gestao.pack_forget()
        self.frame_tabela_gestao.pack(fill=BOTH, expand=YES)
        self.btn_ver_tabela.config(bootstyle="success")
        self.btn_ver_dashboard.config(bootstyle="info-outline")
        self.btn_ver_ressarcimento.config(bootstyle="info-outline")
    def _mostrar_view_dashboard(self):
        self.frame_tabela_gestao.pack_forget()
        self.frame_dashboard_ressarcimento_gestao.pack_forget()
        self.frame_dashboard_geral_gestao.pack(fill=BOTH, expand=YES)
        self.btn_ver_tabela.config(bootstyle="primary-outline")
        self.btn_ver_dashboard.config(bootstyle="success")
        self.btn_ver_ressarcimento.config(bootstyle="info-outline")
    def _mostrar_view_ressarcimento(self):
        self.frame_tabela_gestao.pack_forget()
        self.frame_dashboard_geral_gestao.pack_forget()
        self.frame_dashboard_ressarcimento_gestao.pack(fill=BOTH, expand=YES)
        self.btn_ver_tabela.config(bootstyle="primary-outline")
        self.btn_ver_dashboard.config(bootstyle="info-outline")
        self.btn_ver_ressarcimento.config(bootstyle="success")

    def _get_filtros_gestao(self):
        ano = self.combo_ano_gestao.get()
        mes_str = self.combo_mes_gestao.get()
        cliente = self.combo_cliente_gestao.get()
        produto = self.combo_produto_gestao.get()
        
        filtros = {}
        if ano and ano != "Todos": filtros['ano'] = ano
        if mes_str and mes_str != "Todos":
            mes_map = {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}
            filtros['mes'] = mes_map.get(mes_str)
        if cliente and cliente != "Todos": filtros['cliente'] = cliente
        if produto and produto != "Todos": filtros['produto'] = produto
        return filtros
    
    def _atualizar_aba_gestao(self):
        filtros = self._get_filtros_gestao()
        self._carregar_dados_tabela_gestao(filtros)
        self._desenhar_grafico_geral_e_stats(filtros)
        self._desenhar_grafico_ressarcimento(filtros)

    def _carregar_dados_tabela_gestao(self, filtros):
        for i in self.tree_gestao.get_children(): self.tree_gestao.delete(i)
        dados = db_manager.buscar_dados_completos_para_gestao(filtros)
        for item in dados:
            data_lanc = datetime.strptime(item['data_lancamento'], '%Y-%m-%d').strftime('%d/%m/%Y') if item['data_lancamento'] else '-'
            data_nota = datetime.strptime(item['data_nota'], '%Y-%m-%d').strftime('%d/%m/%Y') if item['data_nota'] else '-'
            valor = f"R$ {item['valor_item']:.2f}" if item['valor_item'] is not None else '-'
            self.tree_gestao.insert('', END, values=(item['id'], data_lanc, item['numero_nota'], data_nota, item['cnpj'] or '-', item['nome_cliente'] or '-', item['grupo_cliente'] or '-', item['codigo_analise'] or '-', item['codigo_produto'] or '-', item['grupo_estoque'] or '-', item['codigo_avaria'] or '-', valor, item['status'] or '-', item['procedente_improcedente'] or '-', item['ressarcimento'] or '-'))
            
# main.py

    def _desenhar_grafico_geral_e_stats(self, filtros):
        for widget in self.frame_grafico_geral_canvas.winfo_children():
            widget.destroy()
        stats = db_manager.obter_estatisticas_garantia(filtros)
        proc_qtd, proc_val = stats['Procedente']['quantidade'], stats['Procedente']['valor_total']
        improc_qtd, improc_val = stats['Improcedente']['quantidade'], stats['Improcedente']['valor_total']
        pend_qtd, pend_val = stats['Pendente']['quantidade'], stats['Pendente']['valor_total']
        total_qtd = proc_qtd + improc_qtd + pend_qtd
        total_val = proc_val + improc_val + pend_val
        self.label_procedente_qtd.config(text=f"Quantidade: {proc_qtd}")
        self.label_procedente_valor.config(text=f"Valor Total: R$ {proc_val:.2f}")
        self.label_improcedente_qtd.config(text=f"Quantidade: {improc_qtd}")
        self.label_improcedente_valor.config(text=f"Valor Total: R$ {improc_val:.2f}")
        self.label_pendente_qtd.config(text=f"Quantidade: {pend_qtd}")
        self.label_pendente_valor.config(text=f"Valor Total: R$ {pend_val:.2f}")
        self.label_total_qtd.config(text=f"Quantidade Total: {total_qtd}")
        self.label_total_valor.config(text=f"Valor Total: R$ {total_val:.2f}")
        labels, sizes, colors = ['Procedentes', 'Improcedentes', 'Pendentes'], [proc_qtd, improc_qtd, pend_qtd], ['#28a745', '#dc3545', '#6c757d']
        non_zero_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
        if not non_zero_data:
            ttk.Label(self.frame_grafico_geral_canvas, text="Não há dados para exibir.").pack(pady=20)
            return
        sizes, labels, colors = zip(*non_zero_data)
        
        # Reduzindo um pouco o tamanho da figura para melhor encaixe
        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
        fig.patch.set_facecolor('#ffffff')
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
        ax.axis('equal')
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico_geral_canvas)
        canvas.draw()
        
        # --- ALTERAÇÃO AQUI ---
        # Remove 'fill=BOTH' para impedir que o gráfico se estique e deforme
        canvas.get_tk_widget().pack(expand=YES)

    # main.py
        
    def _desenhar_grafico_ressarcimento(self, filtros):
        for widget in self.frame_grafico_ressarcimento_canvas.winfo_children():
            widget.destroy()
            
        stats = db_manager.obter_estatisticas_ressarcimento(filtros)
        proc_qtd, proc_val = stats['Procedente']['quantidade'], stats['Procedente']['valor_total']
        improc_qtd, improc_val = stats['Improcedente']['quantidade'], stats['Improcedente']['valor_total']
        pend_qtd, pend_val = stats['Pendente']['quantidade'], stats['Pendente']['valor_total']
        total_qtd = proc_qtd + pend_qtd
        total_val = proc_val + improc_val + pend_val
        self.label_ressarc_proc_qtd.config(text=f"Quantidade: {proc_qtd}")
        self.label_ressarc_proc_valor.config(text=f"Valor Total: R$ {proc_val:.2f}")
        self.label_ressarc_improc_qtd.config(text=f"Quantidade: {improc_qtd}")
        self.label_ressarc_improc_valor.config(text=f"Valor Total: R$ {improc_val:.2f}")
        self.label_ressarc_pend_qtd.config(text=f"Quantidade: {pend_qtd}")
        self.label_ressarc_pend_valor.config(text=f"Valor Potencial: R$ {pend_val:.2f}")
        self.label_total_ressarc_qtd.config(text=f"Quantidade Total: {total_qtd}")
        self.label_total_ressarc_valor.config(text=f"Valor Total: R$ {total_val:.2f}")
        labels, sizes, colors = ['Procedentes', 'Improcedentes', 'Pendentes (Potencial)'], [proc_val, improc_val, pend_val], ['#28a745', '#dc3545', '#ffc107']
        non_zero_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
        
        if not non_zero_data:
            ttk.Label(self.frame_grafico_ressarcimento_canvas, text="Não há dados de ressarcimento para exibir.").pack(pady=20)
            return
            
        sizes, labels, colors = zip(*non_zero_data)

        # Reduzindo um pouco o tamanho da figura para melhor encaixe
        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
        fig.patch.set_facecolor('#ffffff')
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
        ax.axis('equal')
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico_ressarcimento_canvas)
        canvas.draw()
        
        # --- ALTERAÇÃO AQUI ---
        # Remove 'fill=BOTH' para impedir que o gráfico se estique e deforme
        canvas.get_tk_widget().pack(expand=YES)

# ... (restante do arquivo) ...
    def _populate_filtros_gestao(self):
        self.combo_ano_gestao['values'] = ["Todos"] + db_manager.obter_anos_disponiveis()
        self.combo_ano_gestao.set("Todos")
        self.combo_mes_gestao.set("Todos")
        self.combo_cliente_gestao['values'] = ["Todos"] + db_manager.obter_nomes_clientes()
        self.combo_cliente_gestao.set("Todos")
        self.combo_produto_gestao['values'] = ["Todos"] + db_manager.obter_codigos_produtos()
        self.combo_produto_gestao.set("Todos")
        
    def _on_filtro_gestao_aplicar(self):
        self._atualizar_aba_gestao()
        
    def _on_filtro_gestao_limpar(self):
        self.combo_ano_gestao.set("Todos")
        self.combo_mes_gestao.set("Todos")
        self.combo_cliente_gestao.set("Todos")
        self.combo_produto_gestao.set("Todos")
        self._atualizar_aba_gestao()
        
    def _carregar_dados_iniciais(self):
        empresas_do_banco = db_manager.buscar_todas_empresas()
        if empresas_do_banco: self.empresa_combo.set(empresas_do_banco[0])
        self.empresa_combo['values'] = empresas_do_banco
        self.carregar_itens_pendentes()
        self.codigos_avaria_map = db_manager.buscar_todos_codigos_avaria()
        self.analise_avaria_combo['values'] = list(self.codigos_avaria_map.keys())
        self.limpar_form_analise()
        self.aplicar_filtros()
        self._populate_filtros_gestao()
        self._atualizar_aba_gestao()

# ... (CLASSE EDITORWINDOW COMPLETA AQUI) ...
# main.py

class EditorWindow(tk.Toplevel):
    def __init__(self, parent, id_item, avaria_map):
        super().__init__(parent)
        self.parent = parent
        self.id_item = id_item
        self.codigos_avaria_map = avaria_map
        self.title(f"Editar Item de Garantia - ID: {id_item}")
        self.geometry("700x400") # Altura pode ser reduzida
        self.transient(parent)
        self.grab_set()
        form_frame = ttk.LabelFrame(self, text="Dados da Análise", padding=15)
        form_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        form_frame.columnconfigure(1, weight=1); form_frame.columnconfigure(3, weight=1)
        ttk.Label(form_frame, text="Cód. Análise:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cod_entry = ttk.Entry(form_frame, state="readonly"); self.cod_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Nº de Série:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.serie_entry = ttk.Entry(form_frame); self.serie_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Cód. Avaria:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.avaria_combo = ttk.Combobox(form_frame, state="readonly", values=list(self.codigos_avaria_map.keys()))
        self.avaria_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.avaria_combo.bind("<<ComboboxSelected>>", self.atualizar_status)
        self.status_label = ttk.Label(form_frame, text="Status: -", font=("Helvetica", 10, "bold"))
        self.status_label.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        ttk.Label(form_frame, text="Descrição Avaria:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.desc_avaria_entry = ttk.Entry(form_frame, state="readonly")
        self.desc_avaria_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Origem:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.origem_combo = ttk.Combobox(form_frame, state="readonly", values=["Produzido", "Revenda"])
        self.origem_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Fornecedor:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.fornecedor_entry = ttk.Entry(form_frame)
        self.fornecedor_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")
        
        # Campo de Ressarcimento REMOVIDO
        
        save_btn = ttk.Button(form_frame, text="Salvar Alterações", command=self.salvar_edicao, bootstyle="primary")
        save_btn.grid(row=4, column=3, padx=5, pady=20, sticky="e") # Linha ajustada para 4
        self.carregar_dados_item()

    def carregar_dados_item(self):
        item_data = db_manager.buscar_detalhes_completos_item(self.id_item)
        if not item_data: Messagebox.show_error("Não foi possível carregar os dados do item.", "Erro"); self.destroy(); return
        self.cod_entry.config(state="normal")
        self.cod_entry.delete(0, END)
        self.cod_entry.insert(0, item_data['codigo_analise'] or '')
        self.cod_entry.config(state="readonly")
        self.serie_entry.insert(0, item_data['numero_serie'] or '')
        self.avaria_combo.set(item_data['codigo_avaria'] or '')
        self.origem_combo.set(item_data['produzido_revenda'] or '')
        self.fornecedor_entry.insert(0, item_data['fornecedor'] or '')
        # Linha que preenchia o ressarcimento foi REMOVIDA
        self.atualizar_status()

    def atualizar_status(self, event=None):
        cod_avaria = self.avaria_combo.get()
        info = self.codigos_avaria_map.get(cod_avaria, {})
        classificacao = info.get('classificacao', '-')
        self.desc_avaria_entry.config(state="normal")
        self.desc_avaria_entry.delete(0, END)
        self.desc_avaria_entry.insert(0, info.get('descricao', ''))
        self.desc_avaria_entry.config(state="readonly")
        self.status_label.config(text=f"Status: {classificacao}", bootstyle="success" if classificacao == "Procedente" else "danger" if classificacao == "Improcedente" else "default")

    def salvar_edicao(self):
        cod_avaria = self.avaria_combo.get()
        # 'ressarcimento' foi REMOVIDO do dicionário
        dados = {
            'codigo_analise': self.cod_entry.get(),
            'numero_serie': self.serie_entry.get(),
            'codigo_avaria': cod_avaria,
            'descricao_avaria': self.desc_avaria_entry.get(),
            'procedente_improcedente': self.codigos_avaria_map.get(cod_avaria, {}).get('classificacao'),
            'produzido_revenda': self.origem_combo.get(),
            'fornecedor': self.fornecedor_entry.get()
        }
        sucesso, msg = db_manager.salvar_analise_item(self.id_item, dados)
        if sucesso: 
            Messagebox.show_info("Alterações guardadas com sucesso!", "Sucesso")
            self.parent.aplicar_filtros()
            self.parent.carregar_itens_pendentes()
            self.parent._atualizar_aba_gestao()
            self.destroy()
        else: 
            Messagebox.show_error(msg, "Erro ao Guardar")

if __name__ == "__main__":
    sns.set_style("whitegrid")
    app = App()
    app.mainloop()