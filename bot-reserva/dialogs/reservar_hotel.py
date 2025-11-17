import json
import requests
from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    PromptOptions,
    ChoicePrompt
)
from botbuilder.dialogs.choices import Choice, ListStyle
from config import DefaultConfig

CONFIG = DefaultConfig()


class ReservarHotelDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ReservarHotelDialog, self).__init__("ReservarHotelDialog")

        self.user_state = user_state

        # PROMPTS
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        choice_prompt = ChoicePrompt(ChoicePrompt.__name__)
        choice_prompt.style = ListStyle.suggested_action
        self.add_dialog(choice_prompt)

        # DIALOG STEPS
        self.add_dialog(
            WaterfallDialog(
                "ReservarHotelDialog",
                [
                    self.prompt_nome_step,
                    self.prompt_email_step,
                    self.prompt_celular_step,
                    self.prompt_cpf_step,
                    self.prompt_cidade_step,
                    self.prompt_hotel_step,
                    self.prompt_data_entrada_step,
                    self.prompt_data_saida_step,
                    self.confirmar_reserva_step,
                    self.processar_reserva_step,
                    self.final_step
                ]
            )
        )

        self.initial_dialog_id = "ReservarHotelDialog"

    # ================================
    # 1 — NOME
    # ================================
    async def prompt_nome_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity(
            MessageFactory.text("Vamos realizar sua reserva de hotel!")
        )

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Por favor, informe seu nome completo:"))
        )

    # ================================
    # 2 — EMAIL
    # ================================
    async def prompt_email_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["nome"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Informe seu email para contato:"))
        )

    # ================================
    # 3 — CELULAR
    # ================================
    async def prompt_celular_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["email"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Informe seu número de celular (ex: 21999998888):"))
        )

    # ================================
    # 4 — CPF
    # ================================
    async def prompt_cpf_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["celular"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Informe seu CPF (apenas números):"))
        )

    # ================================
    # 5 — CIDADE (TEXTO, NÃO CHOICE)
    # ================================
    async def prompt_cidade_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["cpf"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Para qual cidade você deseja viajar? (ex: Rio de Janeiro)"
                )
            )
        )

    # ================================
    # 6 — HOTEL (CHOICE)
    # ================================
    async def prompt_hotel_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["cidade"] = step_context.result

        try:
            response = requests.get(f"{CONFIG.API_BASE_URL}/opcoes/hoteis")
            hoteis_por_cidade = response.json()
            hoteis = hoteis_por_cidade.get(step_context.values["cidade"], [])
        except:
            hoteis = ["Hotel A", "Hotel B", "Hotel C"]

        options = [Choice(value=hotel) for hotel in hoteis]

        if len(options) == 0:
            options = [Choice("Hotel A"), Choice("Hotel B"), Choice("Hotel C")]

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Qual hotel você prefere?"),
                choices=options,
                style=ListStyle.suggested_action
            )
        )

    # ================================
    # 7 — DATA DE ENTRADA
    # ================================
    async def prompt_data_entrada_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["hotel"] = step_context.result.value

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Data de check-in (DD/MM/AAAA):"))
        )

    # ================================
    # 8 — DATA DE SAÍDA
    # ================================
    async def prompt_data_saida_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["data_entrada"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Data de check-out (DD/MM/AAAA):"))
        )

    # ================================
    # 9 — CONFIRMAR RESERVA
    # ================================
    async def confirmar_reserva_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["data_saida"] = step_context.result

        resumo = (
            f"**Resumo da reserva:**\n\n"
            f"**Nome:** {step_context.values['nome']}\n"
            f"**Email:** {step_context.values['email']}\n"
            f"**Celular:** {step_context.values['celular']}\n"
            f"**CPF:** {step_context.values['cpf']}\n"
            f"**Cidade:** {step_context.values['cidade']}\n"
            f"**Hotel:** {step_context.values['hotel']}\n"
            f"**Check-in:** {step_context.values['data_entrada']}\n"
            f"**Check-out:** {step_context.values['data_saida']}\n\n"
            f"Confirma a reserva?"
        )

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(resumo),
                choices=[Choice("Sim"), Choice("Não")],
                style=ListStyle.suggested_action
            )
        )

    # ================================
    # 10 — PROCESSAR RESERVA
    # ================================
    async def processar_reserva_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        if step_context.result.value == "Sim":

            # Separar datas
            try:
                d1 = step_context.values["data_entrada"].split("/")
                d2 = step_context.values["data_saida"].split("/")

                data_entrada_iso = f"{d1[2]}-{d1[1]}-{d1[0]}"
                data_saida_iso = f"{d2[2]}-{d2[1]}-{d2[0]}"

                payload = {
                    "cliente": {
                        "nome": step_context.values["nome"],
                        "email": step_context.values["email"],
                        "celular": step_context.values["celular"],
                        "cpf": step_context.values["cpf"],
                    },
                    "cidade": step_context.values["cidade"],
                    "hotel": step_context.values["hotel"],
                    "dataEntrada": data_entrada_iso,
                    "dataSaida": data_saida_iso
                }

                response = requests.post(
                    f"{CONFIG.API_BASE_URL}/reservas-hotel",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 201):
                    await step_context.context.send_activity(
                        MessageFactory.text("✅ Sua reserva foi confirmada!")
                    )
                else:
                    await step_context.context.send_activity(
                        MessageFactory.text(
                            f"❌ Erro ao confirmar reserva. Código {response.status_code}"
                        )
                    )

            except Exception:
                await step_context.context.send_activity(
                    MessageFactory.text("❌ Erro no formato de data.")
                )

        else:
            await step_context.context.send_activity(
                MessageFactory.text("Reserva cancelada.")
            )

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("O que deseja fazer agora?"),
                choices=[
                    Choice("Voltar ao menu principal"),
                    Choice("Fazer outra reserva de hotel")
                ],
                style=ListStyle.suggested_action
            )
        )

    # ================================
    # 11 — FINAL STEP
    # ================================
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        escolha = step_context.result.value

        if escolha == "Fazer outra reserva de hotel":
            return await step_context.replace_dialog(self.id)

        return await step_context.end_dialog()
