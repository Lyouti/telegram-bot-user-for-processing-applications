from language_model import llm
import os

print(dict(llm.llm_response("217 кабинет, Петрова Светлана Алексеевна. Компьютер не загружается — после включения чёрный экран и писк. Пробовала отключить питание и включить заново — безрезультатно")))

# script_dir = os.path.dirname(os.path.abspath(__file__))
# print(f"Script directory: {script_dir}")
