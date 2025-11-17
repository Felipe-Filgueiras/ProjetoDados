import json
import requests
from datetime import datetime
from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.dialogs.choices import Choice, ListStyle
from config import DefaultConfig

CONFIG = DefaultConfig()

class ConsultarReservasDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ConsultarReservasDialog, self).__init__("ConsultarReservasDialog")
        
        self.user_state = user_state
        
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        choice_prompt = ChoicePrompt(ChoicePrompt.__name__)
        choice_prompt.style = ListStyle.suggested_action
        self.add_dialog(choice_prompt)

        self.add_dialog(
            WaterfallDialog(
                "ConsultarReservasDialog",
                [
                    self.prompt_cpf_step,
                    self.prompt_tipo_reserva_step,
                    self.process_consulta_step,
                    self.final_step
                ]
            )
        )
                
        self.initial_dialog_id = "ConsultarReservasDialog"
        
    async def prompt_cpf_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Por favor, digite seu CPF para consultar suas reservas:"))
        )
    
    async def prompt_tipo_reserva_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["cpf"] = step_context.result
        
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Qual tipo de reserva você deseja consultar?"),
                choices=[Choice("Hotéis"), Choice("Voos"), Choice("Ambos")],
                style=ListStyle.suggested_action
            )
        )
    
    async def process_consulta_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        tipo_reserva = step_context.result.value
        cpf = step_context.values["cpf"]

        await step_context.context.send_activity(f"Consultando reservas para o CPF: {cpf}...")

        reservas_hotel = []
        reservas_voo = []
        encontrou_reservas = False
        
        # 🔵 CONSULTA DE HOTEL — CORRIGIDA
        if tipo_reserva in ["Hotéis", "Ambos"]:
            try:
                response = requests.get(f"{CONFIG.API_BASE_URL}/reservas-hotel?cpf={cpf}")
                if response.status_code == 200:
                    reservas_hotel = response.json()
            except:
                await step_context.context.send_activity("❌ Não foi possível conectar ao sistema de reservas de hotéis.")
        
        # ✈ CONSULTA DE VOO — CORRIGIDA
        if tipo_reserva in ["Voos", "Ambos"]:
            try:
                response = requests.get(f"{CONFIG.API_BASE_URL}/reservas-voo?cpf={cpf}")
                if response.status_code == 200:
                    reservas_voo = response.json()
            except:
                await step_context.context.send_activity("❌ Não foi possível conectar ao sistema de reservas de voos.")
        
        # Exibir resultados
        if (tipo_reserva in ["Hotéis", "Ambos"] and reservas_hotel) or \
           (tipo_reserva in ["Voos", "Ambos"] and reservas_voo):

            await step_context.context.send_activity("📋 Aqui estão suas reservas:")
            encontrou_reservas = True
            
            # HOTÉIS
            if tipo_reserva in ["Hotéis", "Ambos"]:
                if reservas_hotel:
                    for i, reserva in enumerate(reservas_hotel):
                        data_entrada = reserva.get("dataEntrada")
                        data_saida = reserva.get("dataSaida")

                        mensagem = (
                            f"🏨 **Reserva de Hotel #{i+1}**\n"
                            f"Hotel: {reserva.get('hotel', 'N/A')}\n"
                            f"Cidade: {reserva.get('cidade', 'N/A')}\n"
                            f"Check-in: {data_entrada}\n"
                            f"Check-out: {data_saida}\n"
                        )
                        await step_context.context.send_activity(mensagem)
                else:
                    await step_context.context.send_activity("Você não possui reservas de hotéis.")
            
            # VOOS
            if tipo_reserva in ["Voos", "Ambos"]:
                if reservas_voo:
                    for i, reserva in enumerate(reservas_voo):
                        data = reserva.get("data")

                        mensagem = (
                            f"✈ **Reserva de Voo #{i+1}**\n"
                            f"Código do voo: {reserva.get('codigoVoo', 'N/A')}\n"
                            f"Origem: {reserva.get('cidadeOrigem', 'N/A')}\n"
                            f"Destino: {reserva.get('cidadeDestino', 'N/A')}\n"
                            f"Data: {data}\n"
                            f"Horário: {reserva.get('horario', 'N/A')}\n"
                        )
                        await step_context.context.send_activity(mensagem)
                else:
                    await step_context.context.send_activity("Você não possui reservas de voos.")
        
        # Nenhuma reserva encontrada
        if not encontrou_reservas:
            await step_context.context.send_activity("❌ Não encontramos reservas para este CPF.")
            
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("O que você deseja fazer agora?"),
                choices=[Choice("Voltar ao menu principal"), Choice("Nova consulta")],
                style=ListStyle.suggested_action
            )
        )
    
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        escolha = step_context.result.value
        
        if escolha == "Nova consulta":
            return await step_context.replace_dialog(self.id)
        
        return await step_context.end_dialog()
