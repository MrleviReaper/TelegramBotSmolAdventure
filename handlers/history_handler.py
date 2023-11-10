# обработчики для выбора истории

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import keyboards
from states import HistoryStates
import consts
from handlers.history_texts import *

router = Router()


@router.message(HistoryStates.setting_history, F.text == "Назад")
async def escape_to_menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Сделайте выбор...", reply_markup=keyboards.create_start_kb())


@router.message(HistoryStates.setting_history, F.text.in_(consts.HISTORIES))
async def setting_history(msg: Message, state: FSMContext):
    num = consts.HISTORIES.index(msg.text) + 1
    await state.update_data(history=num)
    await msg.answer(f"Выбрано {msg.text}. Для старта нажмите Начать",
                     reply_markup=keyboards.preparing_for_history_kb())
    await state.set_state(HistoryStates.preparing_for_history)


@router.message(HistoryStates.preparing_for_history, F.text == "Начать")
async def start_history(msg: Message, state: FSMContext):
    num = (await state.get_data())['history']
    await state.set_state(HistoryStates.history_passing)
    await state.update_data(text=iter(eval(f"text{num}")))
    await next_information(msg, state)


@router.message(HistoryStates.history_passing, F.text == "Далее")
async def next_information(msg: Message, state: FSMContext):
    try:
        text = (await state.get_data())["text"]
        await msg.answer(next(text), reply_markup=keyboards.next_kb())
    except StopIteration:
        await msg.answer("Рассказ завершен. Пожалуйста, пройди тест!", reply_markup=keyboards.lets_go_kb())
        await state.set_state(HistoryStates.quiz_passing_preparing)


@router.message(HistoryStates.preparing_for_history, F.text == "Назад")
async def escape_to_history_menu(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, выбери предмет изучения", reply_markup=keyboards.setting_history_kb())
    await state.set_state(HistoryStates.setting_history)


@router.message(HistoryStates.quiz_passing_preparing, F.text == "Вперёд!")
async def start_quiz(msg: Message, state: FSMContext):
    num = (await state.get_data())['history']
    await state.set_state(HistoryStates.quiz_passing)
    await state.update_data(quiz=iter(eval(f"quiz{num}")), answers=[])
    await next_quiz_question(msg, state)


async def next_quiz_question(msg: Message, state: FSMContext):
    try:
        quiz = (await state.get_data())["quiz"]
        question = next(quiz)
        answers = eval(f"quiz{(await state.get_data())['history']}")[question]
        right = answers[4]
        text = f"{question}\n{'А. ' + answers[0]}\n{'Б. ' + answers[1]}\n{'В. ' + answers[2]}\n{'Г. ' + answers[3]}"
        await state.update_data(answer=right)
        await msg.answer(text, reply_markup=keyboards.answer_quiz_kb())
    except StopIteration:
        text = "Результат:\n"
        score = 0
        for right, usr in (await state.get_data())['answers']:
            if right == usr:
                s = ":)"
                score += 1
            else:
                s = ":("
            s += f"Ваш ответ: {usr}; правильный ответ: {right}\n"
            text += s
        text = text[:10] + f" {score * 10}%" + text[10:]
        await msg.answer(text)


@router.message(HistoryStates.quiz_passing, F.text.in_(("А", "Б", "В", "Г")))
async def check_answer(msg: Message, state: FSMContext):
    ans = (await state.get_data())['answer']
    sp = (await state.get_data())['answers']
    sp.append((ans, msg.text))
    await state.update_data(answers=sp)
    await next_quiz_question(msg, state)
