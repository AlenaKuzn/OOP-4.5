#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import date
import logging
import sys
from typing import List
import xml.etree.ElementTree as ET


# Класс пользовательского исключения в случае, если введенная
# команда является недопустимой.
class UnknownCommandError(Exception):
   def __init__(self, command, message = "Unknown command"):
       self.command = command
       self.message = message
       super(UnknownCommandError, self).__init__(message)
   def __str__(self):
       return f"{self.command} -> {self.message}"


@dataclass(frozen=True)
class re:
   pynkt: str
   numb: int
   samolet: str


@dataclass
class Staff:
   reys: List[re] = field(default_factory=lambda: [])

   def add(self, pynkt: str, numb: int, samolet: str) -> None:
       self.reys.append(re(pynkt=pynkt, numb=numb, samolet=samolet))
       self.reys.sort(key=lambda re: re.pynkt)


   def __str__(self):
       # Заголовок таблицы.
       table = []
       line = '+-{}-+-{}-+-{}-+-{}-+'.format(
           '-' * 4,
           '-' * 30,
           '-' * 20,
           '-' * 8
       )
       table.append(line)
       table.append(
           '| {:^4} | {:^30} | {:^20} | {:^8} |'.format(
               "№",
               "Пункт",
               "Номер рейса",
               "Самолет"
           )
       )
       table.append(line)

       # Вывести данные о всех сотрудниках.
       for idx, re in enumerate(self.reys, 1):
           table.append(
               '| {:>4} | {:<30} | {:<20} | {:>8} |'.format(
                   idx,
                   re.pynkt,
                   re.numb,
                   re.samolet
               )
           )

       table.append(line)
       return '\n'.join(table)


   def select(self, pynkt_pr: str) -> List[re]:
       result = []
       for employee in self.reys:
            if employee.get('pynkt') == pynkt_pr:
                result.append(employee)

       return result


   def load(self, filename: str) -> None:
       with open(filename, 'r', encoding='utf8') as fin:
           xml = fin.read()

       parser = ET.XMLParser(encoding="utf8")
       tree = ET.fromstring(xml, parser=parser)

       self.reys = []
       for re_element in tree:
           pynkt, numb, samolet = None, None, None

           for element in re_element:
               if element.tag == 'pynkt':
                   pynkt = element.text
               elif element.tag == 'numb':
                   numb = int(element.text)
               elif element.tag == 'samolet':
                   samolet = element.text


   def save(self, filename: str) -> None:
       root = ET.Element('reys')
       for re in self.reys:
           reys_element = ET.Element('reys')

           pynkt_element = ET.SubElement(reys_element, 'pynkt')
           pynkt_element.text = re.pynkt

           numb_element = ET.SubElement(reys_element, 'numb')
           numb_element.text = str(re.numb)

           samolet_element = ET.SubElement(reys_element, 'samolet')
           samolet_element.text = re.samolet

           root.append(reys_element)

       tree = ET.ElementTree(root)

       with open(filename, 'wb') as fout:
           tree.write(fout, encoding='utf8', xml_declaration=True)


if __name__ == '__main__':
   # Выполнить настройку логгера.
   logging.basicConfig(
       filename='reys.log',
       level=logging.INFO
  )

   # Список работников.
   staff = Staff()

   # Организовать бесконечный цикл запроса команд.
   while True:
       try:
           # Запросить команду из терминала.
           command = input(">>> ").lower()

           # Выполнить действие в соответствие с командой.
           if command == 'exit':
               break

           elif command == 'add':
               # Запросить данные о рейсе.
               pynkt = input("Пункт назвачения: ")
               numb = int(input("Номер рейса: "))
               samolet = input("Тип самолета ")

               staff.add(pynkt, numb, samolet)
               logging.info(
                   f"Добавлен рейс: {pynkt}, {numb}, "
                   f"тип самолета {samolet}"
               )

           elif command == 'list':
               # Вывести список.
               print(staff)
               logging.info("Отображен список рейсов.")

           elif command.startswith('select '):
               # Разбить команду на части для выделения номера года.
               parts = command.split(maxsplit=1)
               # Запросить работников.
               selected = staff.select(parts[1])

               # Вывести результаты запроса.
               if selected:
                   for idx, re in enumerate(selected, 1):
                       print(
                           '{:>4}: {}'.format(idx, re.pynkt)
                       )
                   logging.info(
                       f"Найдено {len(selected)} рейсов "
                       f"из пункта {parts[1]}"
                   )
               else:
                   print("Рейс с заданным пунктом не найдет.")

           elif command.startswith('load '):
                # Разбить команду на части для имени файла.
                parts = command.split(maxsplit=1)
                # Загрузить данные из файла.
                staff.load(parts[1])
                logging.info(f"Загружены данные из файла {parts[1]}.")

           elif command.startswith('save '):
                # Разбить команду на части для имени файла.
                parts = command.split(maxsplit=1)
                # Сохранить данные в файл.
                staff.save(parts[1])
                logging.info(f"Сохранены данные в файл {parts[1]}.")

           elif command == 'help':
                # Вывести справку о работе с программой.
                print("Список команд:\n")
                print("add - добавить данные о рейсе;")
                print("list - вывести список рейсов;")
                print("select <стаж> - запросить работников со стажем;")
                print("load <имя_файла> - загрузить данные из файла;")
                print("save <имя_файла> - сохранить данные в файл;")
                print("help - отобразить справку;")
                print("exit - завершить работу с программой.")

           else:
               raise UnknownCommandError(command)

       except Exception as exc:
           logging.error(f"Ошибка: {exc}")
           print(exc, file=sys.stderr)
