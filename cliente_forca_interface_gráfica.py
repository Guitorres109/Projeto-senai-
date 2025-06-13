import asyncio
import threading
import tkinter as tk
import websockets

class ClienteForcaGUI:
    def __init__(self, master):
        self.master = master
        master.title("Jogo da Forca - Cliente")
        master.configure(bg="#2c3e50")

        self.frame = tk.Frame(master, bg="#34495e", bd=0)
        self.frame.pack(padx=20, pady=20)

        self.chat_frame = tk.Frame(self.frame, bg="#34495e")
        self.chat_frame.pack(side='left', pady=(0, 10))

        self.chat = tk.Text(
            self.chat_frame, height=15, width=40, state='disabled', wrap='word',
            bg="#2c3e50", fg="white", bd=0, highlightthickness=0, font=("Consolas", 12),
            padx=10, pady=10
        )
        self.chat.pack(side='left')

        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.chat.config(yscrollcommand=self.scrollbar.set)

        self.canvas = tk.Canvas(
            self.frame, width=200, height=250, bg="#34495e", bd=0, highlightthickness=0
        )
        self.canvas.pack(side='left', padx=(15,0))
        self.canvas.config(highlightbackground="#ecf0f1")

        self.bottom_frame = tk.Frame(master, bg="#2c3e50")
        self.bottom_frame.pack(pady=(10, 0))

        self.entry = tk.Entry(
            self.bottom_frame, width=40, font=("Consolas", 14), 
            bg="#ecf0f1", fg="#2c3e50", bd=0, relief='flat', highlightthickness=1, highlightbackground="#95a5a6"
        )
        self.entry.pack(side='left', padx=(0, 10), ipady=6)
        self.entry.bind("<Return>", lambda event: self.enviar())

        self.botao = tk.Button(
            self.bottom_frame, text="Enviar", command=self.enviar,
            bg="#1abc9c", fg="white", activebackground="#16a085",
            bd=0, padx=15, pady=6, font=("Consolas", 12, "bold"), cursor="hand2"
        )
        self.botao.pack(side='left')

        # Frame dos botões Sim e Não dentro do bottom_frame
        self.frame_botoes = tk.Frame(self.bottom_frame, bg="#2c3e50")
        self.frame_botoes.pack_forget()  # começa escondido

        self.botao_sim = tk.Button(
            self.frame_botoes, text="Sim", width=10, command=lambda: self.responder_jogo("s"),
            bg="#27ae60", fg="white", bd=0, font=("Consolas", 12, "bold"),
            activebackground="#2ecc71", cursor="hand2"
        )
        self.botao_sim.pack(side='left', padx=10)
        self.botao_sim.bind("<Enter>", lambda e: self.botao_sim.config(bg="#2ecc71"))
        self.botao_sim.bind("<Leave>", lambda e: self.botao_sim.config(bg="#27ae60"))

        self.botao_nao = tk.Button(
            self.frame_botoes, text="Não", width=10, command=lambda: self.responder_jogo("n"),
            bg="#c0392b", fg="white", bd=0, font=("Consolas", 12, "bold"),
            activebackground="#e74c3c", cursor="hand2"
        )
        self.botao_nao.pack(side='left', padx=10)
        self.botao_nao.bind("<Enter>", lambda e: self.botao_nao.config(bg="#e74c3c"))
        self.botao_nao.bind("<Leave>", lambda e: self.botao_nao.config(bg="#c0392b"))

        self.erros = 0
        self.head_pulse_size = 0

        self.uri = "ws://10.0.2.4:8765"
        self.websocket = None
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.iniciar_conexao, daemon=True).start()

        # DEBUG: descomente a linha abaixo para testar se os botões aparecem após 2 segundos
        # self.master.after(2000, lambda: self.frame_botoes.pack(fill='x', pady=10))

    def adicionar_texto(self, texto):
        if texto.lower().startswith("palavra:"):
            self.erros = 0
            self.head_pulse_size = 0
            self.atualizar_boneco(self.erros)
            self.adicionar_texto_normal(texto)

        elif "erros:" in texto.lower():
            try:
                partes = texto.lower().split("erros:")
                erros_atual = int(partes[1].strip())
                if erros_atual > self.erros:
                    self.head_pulse_size = 6
                self.erros = erros_atual
                self.animar_boneco()
            except:
                pass
            self.adicionar_texto_normal(texto)

        elif "Deseja jogar novamente?" in texto:
            self.adicionar_texto_normal("Deseja jogar novamente?")
            self.entry.config(state='disabled')
            self.botao.config(state='disabled')
            self.frame_botoes.pack(fill='x', pady=10)

        else:
            self.adicionar_texto_normal(texto)

    def adicionar_texto_normal(self, texto):
        self.chat.config(state='normal')
        self.chat.insert(tk.END, texto + "\n")
        self.chat.see(tk.END)
        self.chat.config(state='disabled')

    def enviar(self):
        mensagem = self.entry.get().strip()
        if mensagem and self.websocket:
            self.loop.call_soon_threadsafe(self.loop.create_task, self.websocket.send(mensagem))
            self.entry.delete(0, tk.END)

    def responder_jogo(self, resposta):
        if self.websocket:
            self.loop.call_soon_threadsafe(self.loop.create_task, self.websocket.send(resposta))
        self.frame_botoes.pack_forget()
        self.entry.config(state='normal')
        self.botao.config(state='normal')

    def atualizar_boneco(self, erros, pulse_head_offset=0):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 200, 250, fill="#34495e", outline="")

        self.canvas.create_line(20, 230, 180, 230, width=4, fill="#ecf0f1")
        self.canvas.create_line(50, 230, 50, 20, width=4, fill="#ecf0f1")
        self.canvas.create_line(50, 20, 130, 20, width=4, fill="#ecf0f1")
        self.canvas.create_line(130, 20, 130, 40, width=4, fill="#ecf0f1")

        if erros >= 1:
            x0, y0 = 110 - pulse_head_offset, 40 - pulse_head_offset
            x1, y1 = 150 + pulse_head_offset, 80 + pulse_head_offset
            self.canvas.create_oval(x0, y0, x1, y1, width=3, outline="#1abc9c", fill="#16a085")
        if erros >= 2:
            self.canvas.create_line(130, 80, 130, 140, width=3, fill="#1abc9c")
        if erros >= 3:
            self.canvas.create_line(130, 90, 100, 110, width=3, fill="#1abc9c")
        if erros >= 4:
            self.canvas.create_line(130, 90, 160, 110, width=3, fill="#1abc9c")
        if erros >= 5:
            self.canvas.create_line(130, 140, 100, 180, width=3, fill="#1abc9c")
        if erros >= 6:
            self.canvas.create_line(130, 140, 160, 180, width=3, fill="#1abc9c")

    def animar_boneco(self):
        if self.head_pulse_size > 0:
            self.atualizar_boneco(self.erros, self.head_pulse_size)
            self.head_pulse_size -= 1
            self.master.after(50, self.animar_boneco)
        else:
            self.atualizar_boneco(self.erros)

    async def receber_mensagens(self):
        try:
            async with websockets.connect(self.uri) as self.websocket:
                while True:
                    msg = await self.websocket.recv()
                    self.adicionar_texto(msg)
                    if "Obrigado por jogar" in msg:
                        break
        except Exception as e:
            self.adicionar_texto(f"Erro: {str(e)}")

    def iniciar_conexao(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.receber_mensagens())

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x400")
    root.resizable(False, False)
    app = ClienteForcaGUI(root)
    root.mainloop()
