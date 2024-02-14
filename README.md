# Лабораторная работа №3. На кончиках пальцев
___
- Бугаев Сергей Юрьевич
- `alg | acc | neum | mc | tick | struct | stream | port | cstr | prob1 | 8bit`
- Без усложнения

**Описание варианта**
- **alg** -- синтаксис языка должен напоминать java/javascript/lua. Должен поддерживать математические выражения.
- **acc** -- система команд должна быть выстроена вокруг аккумулятора.
  - Инструкции -- изменяют значение, хранимое в аккумуляторе.  
  - Ввод-вывод осуществляется через аккумулятор.
- **neum** -- фон Неймановская архитектура.
- **mc** -- microcoded.
- **tick** -- процессор необходимо моделировать с точностью до такта, процесс моделирования может быть приостановлен на любом такте
- **struct** -- машинный код в виде высокоуровневой структуры данных. Считается, что одна инструкция укладывается в одно машинное слово.
- **stream** -- Ввод-вывод осуществляется как поток токенов.
- **port** -- port-mapped (специальные инструкции для ввода-вывода)
- **cstr** -- Null-terminated (C string)
- **prob1** -- Multiples of 3 or 5
- **8bit** -- машинное слово -- 8 бит (как для памяти команд, так и для памяти данных, если они разделены). - **не реализовано**
___

## Язык программирования

- Описание синтаксиса:
```
<программа> ::= <строка_программы> {<программа>}*

<строка_программы> ::= <объявление_переменной> | <условный_оператор> | <цикл> | <ввод> | <вывод>

<объявление_переменной> ::= [<тип>] ["{"<целочисленная_константа>"}"] <идентификатор> "=" <выражение> ;

<тип> :: = int | str

<идентификатор> ::= {<буква>}*

<выражение> ::= <арифметическое_выражение> | <идентификатор> | <литерал>

<условный_оператор> ::= if "(" <логическое выражение> ")" "{" <тело_оператора> "}"

<логическое выражение> ::= (<идентификатор> (< | > | == ) <целочисленная_константа>) | (<идентификатор> % <целочисленная_константа> == <целочисленная_константа>)

<цикл> ::= while ( <логическое выражение> ) { <тело_оператора> }

<тело_оператора> ::= <программа>

<арифметическое_выражение> ::= <терм> { ( + | - | * | /) <арифметическое_выражение> }*

<терм> ::= <идентификатор> | <литерал>

<литерал> ::= <целочисленная_константа> | <строка>

<целочисленная_константа> ::= <цифра>+

<ввод> ::= read(<идентификатор>);

<вывод> ::= print(<идентификатор>|<строка>);

<строка> ::= '{<любой_символ>}*'

<любой_символ> ::= <буква> | <цифра> | ...

<буква> ::= a | b | c | ... | z | A | B | C | ... | Z

<цифра> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```
**Описание**
- Область видимости: Глобальная
- Статическая типизация.
- Типы данных включают в себя int, str.
- Виды литералов:
  - Целочисленные: 123, 12425
  - Строки: 'asdf', 'hello'
- Поддержка математических выражений ( +, -, *, /) - реализовано с помощью обратной польской нотации
- Код выполняется последовательно
- Переменные хранятся на стеке

## Организация памяти

```
               Registers
+------------------------------------+
| ACC - аккумулятор                  |
+------------------------------------+
| CR - регистр инструкции            |
+------------------------------------+
| DR - регистр данных                |
+------------------------------------+
| IP - счётчик команд                |
+------------------------------------+
| SP - указатель стека               |
+------------------------------------+
| AR - адрес записи в память         |
+------------------------------------+
| IN - Порт для ввода значений       |
+------------------------------------+
| OUT - Порт для вывода значений     |
+------------------------------------+

            Instruction & Data memory
+-----------------------------------------------+
|    0    :  programm start                     |  <-- IP, SP
|        ...                                    |
|        ...                                    |
+-----------------------------------------------+

```
- Память данных и команд общая (фон Нейман)
- Виды адресации:
    - абсолютная
    - непосредственная адресация
    - косвенная
- Назначение регистров
    - ACC -- главный регистр (аккумуляторная архитектура), содержит результаты всех операций, ввод-вывод реализуется с него
    - CR -- содержит текущую выполняемую инструкцию
    - DR -- вспомомогательный регистр, хранит данные для выполнения текущей инструкции (После цикла выборки операнда)
    - IP -- содержит адрес следующей инструкции, которая должна быть выполнена
    - SP -- при операциях push и pop уменьшается и увеличивается соответственно (стек растет снизу вверх)
    - AR -- содержит адрес, по которому произойдет запись или чтение из памяти
- Циклы выполнения команды:
  - Цикл выборки инструкции: 1 такт
  - Цикл выборки операнда: 2-3 такта (Зависит от вида адресации)
  - Цикл выполнения команды: 1-3 такта
- Константы отсутствуют в языке
- Переменные помещаются на стек
- Строковые литералы хранятся последовательно в памяти
- В одном машинном слове хранится 1 символ строкового литерала
## Система команд

Особенности процессора:

- Длина машинного слова не определена
- Доступ к вводу-выводу происходит через специальные команды (1 - Порт для буффера, 2 - Порт для вывода)

Цикл команды:

- Выборка инструкции -- mem[IP] -> CR, IP+1 -> IP
- Выборка операнда --
  - addr-> AR, mem[AR] -> DR (Абсолютная);
  - addr -> DR (Непосредственная);
  - addr -> AR, mem[AR] -> AR, mem[AR] -> DR (косвенная)
- Выполнение команды 


### Набор инструкций

| Инструкция         | Описание                                                                         |
|:-------------------|:---------------------------------------------------------------------------------|
| ST `<addr>`        | Сохранить в память значение из аккумулятора                                      |
| LD  `<addr>`       | Загрузить в аккумулятор значение из памяти                                       |
| ADD `<addr>`       | Сложить значение аккумулятора с значением из памяти, записать в аккумулятор      |
| SUB `<addr>`       | Вычесть из значения аккумулятора значение из памяти, записать в аккумулятор      |
| MUL `<addr>`       | Умножить значение аккумулятора на значение из памяти, записать в аккумулятор     |
| DIV `<addr>`       | Поделить значение аккумулятора на значение из памяти, записать в аккумулятор     |
| JUMP `<addr>`      | перейти по адресу                                                                |
| PUSH               | Сохранить в стек значение аккумулятора                                           |
| NOP                | отсутствие операции                                                              |
| POP                | Загрузить в аккумулятор значение со стека                                        | 
| CMP `<addr>`       | Выставить значения флагов при сравнении аккумулятора и значения из памяти        | 
| JE `<addr>`        | перейти по адресу, если флаг Z == 1                                              |
| JNE `<addr>`       | перейти по адресу, если флаг Z == 0                                              |              
| JA `<addr>`        | перейти по адресу, если флаг N == 0                                              |
| JB `<addr>`        | перейти по адресу, если флаг N == 1                                              |
| HALT               | Остановка симуляции                                                              |
| INC                | Прибавить к аккумулятору 1                                                       |

- `<addr>` -- абсолютная/косвенная/непосредственная адресация

### Кодирование инструкций

- Машинный код сереализуется в список JSON
- Один элемент списка -- одна инструкция

Пример:

```json
[
    {
        "index": 0,
        "opcode": "Opcode.LD",
        "arg1": "#",
        "arg2": 2011
    }
]
```

где:

- `index` -- адрес в памяти
- `opcode` -- код операции
- `arg1` -- вид адрессации
- `arg2` -- аргумент

Типы данных в модуле [isa](machine/isa.py), где:

- `Opcode` -- перечисление кодов операций
- 'TypesOfAddressing' -- доступные виды адресации 
## Транслятор

Интерфейс командной строки: `translator.py <input_file> <target_file>`

Реализовано в модуле: [translator](translator/translate.py)

Этапы трансляции:
1. [Lexer](translator/lexer.py) - разбивает код из <input_file> на токены
2. [AST](translator/ast.py) - используя токены строит абстрактное синтаксическое дерево
3. [translator](translator/translate.py) - используя AST, создаётся машинный код, записывает в виде json в <target_file>

## Модель процессора

Интерфейс командной строки: `machine.py <machine_code_file> <input_file>`

Реализовано в модуле: [machine](machine/processor.py).

**Datapath**

![DataPath](./img/data_path.png)

Реализован в [machine](machine/data_path.py).

Регистры (соответствуют регистрам на схеме):

- `ACC`
- `DR`
- `CR`
- `AR`
- `SP`
- `IP`


Сигналы:
- `latch_ar` -- защелкнуть адресный регистр (addr->AR | mem[AR] -> AR)
- `latch_acc` -- защелкнуть аккумулятор (DR -> ACC | ALU_result -> ACC | mem[sp] -> ACC)
- `latch_ip` -- защелкнуть счетчик команд ( IP+1 -> IP | DR->IP)
- `latch_sp` -- защелкнуть регистр стека (SP+1-> SP | SP-1 -> SP)
- `latch_dr` -- защелкнуть регистр данных
- `latch_cr` -- защелкнуть регистр команд mem[IP] -> CR
- `latch_left_op` -- ACC -> left_operand
- `latch_right_op` -- ACC -> right_operand
- `signal_wr` -- запись в память ACC
- `calculate` -- выполнить операцию на АЛУ
- `get_flags` -- Получить флаги с АЛУ

Селекторы для мультиплексоров реализованы с помощью Enum в [machine](machine/data_path.py) классом Selector

Флаги:
- `N` (negative) -- результат в алу содержит отрицательное число
- `Z` (zero) -- результат в алу содержит ноль

**ControlUnit**

![control_unit](./img/control_unit.png)

Реализован в [machine](machine/control_unit.py).

- Выполняет микрокод:
  - Длина машинного слова микрокода 23
  - Включает в себя сигналы и мультиплексоры для DataPath
  - Хранится в отдельной памяти в Control Unit
  - Названия каждобого бита:
    - **latch_cr** -- защелкнуть адресный регистр
    - **sel_ip** -- Мультиплексор для ip
    - **latch_ip** -- защелкнуть счетчик команд
    - **sel_ar**  -- Мультиплексор для ar
    - **latch_ar** -- защелкнуть адресный регистр
    - **sel_oe** -- Мультиплексор для oe
    - **signal_oe** -- сигнал для чтения
    - **sel_dr** -- Мультиплексор для dr
    - **latch_dr** -- защелкнуть регистр данных
    - **latch_left_op** -- -- ACC -> left_operand
    - **latch_right_op** -- ACC -> right_operand
    - **signal_calculate** -- выполнить операцию на АЛУ
    - **check_flags** -- проверка флагов
    - **sel_acc** -- Мультиплексор для acc
    - **latch_acc** -- защелкнуть аккумулятор
    - **sel_wr** -- Мультиплексор для wr
    - **signal_wr**  -- сигнал на запись в память
    - **sel_sp** -- Мультиплексор для sp
    - **latch_sp** - защелкнуть SP
    - **latch_out** -- Запись в порт для выхода
    - **mux_port** -- Выбор порта 
    - **latch_in** -- Запись в порт для входа
    - **mux_mPC** -- 3 возможных значения
      - +1 -- переход к следующей микрокоманде
      - 0 -- переход к 0 микрокоманде
      - decode - декодировать следующую команду
    - **latch_mPC** -- защёлкнуть счётчик микрокоманд
- Метод `process_tick` моделирует выполнение следующего такта 
- Каждая запись в журнале соответсвует состоянию процессора **после** выполнения инструкции
- Для журнала состояний процессора используется стандартный модуль `logging`
- Количество инструкций для моделирования лимитировано
- Остановка моделирования осуществляется при:
    - превышении лимита количества tick
    - исключении `HaltError` (команда `halt`)
    - Попытке получить данные из пустого буфера

## Тестирование

Реализованные программы:

1. [hello_world](./examples/hello_world.lab3) -- печатаем 'Hello, World!'
1. [cat](./examples/cat.lab3) --  программа cat, повторяем ввод на выводе
1. [hello_usr](./examples/hello_user.lab3) -- запросить у пользователя его имя, считать его, вывести на экран приветствие
1. [prob2](./examples/prob2.lab3) -- сумма четных чисел, не превышающих 4 млн, последовательности Фиббоначи

Интеграционные тесты реализованы в [integration_test](./integration_test.py):

- Стратегия: golden tests, конфигурация в папке [golden/](./golden/)

CI при помощи Github Action:

```yaml
defaults:
  run:
    working-directory: ./

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Run tests and collect coverage
        run: |
          poetry run coverage run -m pytest .
          poetry run coverage report -m
        env:
          CI: true

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Check code formatting with Ruff
        run: poetry run ruff format --check .

      - name: Run Ruff linters
        run: poetry run ruff check .
```

Пример использования и журнал работы процессора на примере hello_world

- Код:
print('hello world!');

- Машинный код:
```
[{"index": 0, "opcode": "Opcode.JUMP", "arg1": "#", "arg2": 14},
  {"index": 1, "opcode": "Opcode.NOP", "arg1": 104, "arg2": null},
  {"index": 2, "opcode": "Opcode.NOP", "arg1": 101, "arg2": null},
  {"index": 3, "opcode": "Opcode.NOP", "arg1": 108, "arg2": null},
  {"index": 4, "opcode": "Opcode.NOP", "arg1": 108, "arg2": null},
  {"index": 5, "opcode": "Opcode.NOP", "arg1": 111, "arg2": null},
  {"index": 6, "opcode": "Opcode.NOP", "arg1": 32, "arg2": null},
  {"index": 7, "opcode": "Opcode.NOP", "arg1": 119, "arg2": null},
  {"index": 8, "opcode": "Opcode.NOP", "arg1": 111, "arg2": null},
  {"index": 9, "opcode": "Opcode.NOP", "arg1": 114, "arg2": null},
  {"index": 10, "opcode": "Opcode.NOP", "arg1": 108, "arg2": null},
  {"index": 11, "opcode": "Opcode.NOP", "arg1": 100, "arg2": null},
  {"index": 12, "opcode": "Opcode.NOP", "arg1": 33, "arg2": null},
  {"index": 13, "opcode": "Opcode.NOP", "arg1": 0, "arg2": null},
  {"index": 14, "opcode": "Opcode.LD", "arg1": "#", "arg2": 1},
  {"index": 15, "opcode": "Opcode.PUSH", "arg1": null, "arg2": null},
  {"index": 16, "opcode": "Opcode.LD", "arg1": "~", "arg2": 8095},
  {"index": 17, "opcode": "Opcode.PRINT", "arg1": null, "arg2": 2},
  {"index": 18, "opcode": "Opcode.CMP", "arg1": "#", "arg2": 0},
  {"index": 19, "opcode": "Opcode.JE", "arg1": "#", "arg2": 24},
  {"index": 20, "opcode": "Opcode.POP", "arg1": null, "arg2": null},
  {"index": 21, "opcode": "Opcode.INC", "arg1": null, "arg2": null},
  {"index": 22, "opcode": "Opcode.PUSH", "arg1": null, "arg2": null},
  {"index": 23, "opcode": "Opcode.JUMP", "arg1": "#", "arg2": 16},
  {"index": 24, "opcode": "Opcode.HALT", "arg1": null, "arg2": null}]
```

- Вывод программы:
hello world!

- Журнал работы:
```
INFO    processor:simulation    Simulation start
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:          4 | ip:         14 | dr         14 |ar:          0 | acc:          0 | sp:       8095
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:          8 | ip:         15 | dr          1 |ar:          0 | acc:          1 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:         11 | ip:         16 | dr          1 |ar:          0 | acc:          1 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:         17 | ip:         17 | dr        104 |ar:          1 | acc:        104 | sp:       8094
  DEBUG   datapath:output         <- h
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:         20 | ip:         18 | dr        104 |ar:          1 | acc:        104 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:         24 | ip:         19 | dr          0 |ar:          1 | acc:        104 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:         28 | ip:         20 | dr         24 |ar:          1 | acc:        104 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:         33 | ip:         21 | dr          1 |ar:          1 | acc:          1 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:         36 | ip:         22 | dr          1 |ar:          1 | acc:          2 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:         39 | ip:         23 | dr          1 |ar:          1 | acc:          2 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:         43 | ip:         16 | dr         16 |ar:          1 | acc:          2 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:         49 | ip:         17 | dr        101 |ar:          2 | acc:        101 | sp:       8094
  DEBUG   datapath:output        h <- e
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:         52 | ip:         18 | dr        101 |ar:          2 | acc:        101 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:         56 | ip:         19 | dr          0 |ar:          2 | acc:        101 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:         60 | ip:         20 | dr         24 |ar:          2 | acc:        101 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:         65 | ip:         21 | dr          2 |ar:          2 | acc:          2 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:         68 | ip:         22 | dr          2 |ar:          2 | acc:          3 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:         71 | ip:         23 | dr          2 |ar:          2 | acc:          3 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:         75 | ip:         16 | dr         16 |ar:          2 | acc:          3 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:         81 | ip:         17 | dr        108 |ar:          3 | acc:        108 | sp:       8094
  DEBUG   datapath:output        he <- l
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:         84 | ip:         18 | dr        108 |ar:          3 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:         88 | ip:         19 | dr          0 |ar:          3 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:         92 | ip:         20 | dr         24 |ar:          3 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:         97 | ip:         21 | dr          3 |ar:          3 | acc:          3 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        100 | ip:         22 | dr          3 |ar:          3 | acc:          4 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        103 | ip:         23 | dr          3 |ar:          3 | acc:          4 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        107 | ip:         16 | dr         16 |ar:          3 | acc:          4 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        113 | ip:         17 | dr        108 |ar:          4 | acc:        108 | sp:       8094
  DEBUG   datapath:output        hel <- l
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        116 | ip:         18 | dr        108 |ar:          4 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        120 | ip:         19 | dr          0 |ar:          4 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        124 | ip:         20 | dr         24 |ar:          4 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        129 | ip:         21 | dr          4 |ar:          4 | acc:          4 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        132 | ip:         22 | dr          4 |ar:          4 | acc:          5 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        135 | ip:         23 | dr          4 |ar:          4 | acc:          5 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        139 | ip:         16 | dr         16 |ar:          4 | acc:          5 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        145 | ip:         17 | dr        111 |ar:          5 | acc:        111 | sp:       8094
  DEBUG   datapath:output        hell <- o
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        148 | ip:         18 | dr        111 |ar:          5 | acc:        111 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        152 | ip:         19 | dr          0 |ar:          5 | acc:        111 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        156 | ip:         20 | dr         24 |ar:          5 | acc:        111 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        161 | ip:         21 | dr          5 |ar:          5 | acc:          5 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        164 | ip:         22 | dr          5 |ar:          5 | acc:          6 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        167 | ip:         23 | dr          5 |ar:          5 | acc:          6 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        171 | ip:         16 | dr         16 |ar:          5 | acc:          6 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        177 | ip:         17 | dr         32 |ar:          6 | acc:         32 | sp:       8094
  DEBUG   datapath:output        hello <- ' '
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        180 | ip:         18 | dr         32 |ar:          6 | acc:         32 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        184 | ip:         19 | dr          0 |ar:          6 | acc:         32 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        188 | ip:         20 | dr         24 |ar:          6 | acc:         32 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        193 | ip:         21 | dr          6 |ar:          6 | acc:          6 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        196 | ip:         22 | dr          6 |ar:          6 | acc:          7 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        199 | ip:         23 | dr          6 |ar:          6 | acc:          7 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        203 | ip:         16 | dr         16 |ar:          6 | acc:          7 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        209 | ip:         17 | dr        119 |ar:          7 | acc:        119 | sp:       8094
  DEBUG   datapath:output        hello  <- w
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        212 | ip:         18 | dr        119 |ar:          7 | acc:        119 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        216 | ip:         19 | dr          0 |ar:          7 | acc:        119 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        220 | ip:         20 | dr         24 |ar:          7 | acc:        119 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        225 | ip:         21 | dr          7 |ar:          7 | acc:          7 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        228 | ip:         22 | dr          7 |ar:          7 | acc:          8 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        231 | ip:         23 | dr          7 |ar:          7 | acc:          8 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        235 | ip:         16 | dr         16 |ar:          7 | acc:          8 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        241 | ip:         17 | dr        111 |ar:          8 | acc:        111 | sp:       8094
  DEBUG   datapath:output        hello w <- o
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        244 | ip:         18 | dr        111 |ar:          8 | acc:        111 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        248 | ip:         19 | dr          0 |ar:          8 | acc:        111 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        252 | ip:         20 | dr         24 |ar:          8 | acc:        111 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        257 | ip:         21 | dr          8 |ar:          8 | acc:          8 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        260 | ip:         22 | dr          8 |ar:          8 | acc:          9 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        263 | ip:         23 | dr          8 |ar:          8 | acc:          9 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        267 | ip:         16 | dr         16 |ar:          8 | acc:          9 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        273 | ip:         17 | dr        114 |ar:          9 | acc:        114 | sp:       8094
  DEBUG   datapath:output        hello wo <- r
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        276 | ip:         18 | dr        114 |ar:          9 | acc:        114 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        280 | ip:         19 | dr          0 |ar:          9 | acc:        114 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        284 | ip:         20 | dr         24 |ar:          9 | acc:        114 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        289 | ip:         21 | dr          9 |ar:          9 | acc:          9 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        292 | ip:         22 | dr          9 |ar:          9 | acc:         10 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        295 | ip:         23 | dr          9 |ar:          9 | acc:         10 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        299 | ip:         16 | dr         16 |ar:          9 | acc:         10 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        305 | ip:         17 | dr        108 |ar:         10 | acc:        108 | sp:       8094
  DEBUG   datapath:output        hello wor <- l
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        308 | ip:         18 | dr        108 |ar:         10 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        312 | ip:         19 | dr          0 |ar:         10 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        316 | ip:         20 | dr         24 |ar:         10 | acc:        108 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        321 | ip:         21 | dr         10 |ar:         10 | acc:         10 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        324 | ip:         22 | dr         10 |ar:         10 | acc:         11 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        327 | ip:         23 | dr         10 |ar:         10 | acc:         11 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        331 | ip:         16 | dr         16 |ar:         10 | acc:         11 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        337 | ip:         17 | dr        100 |ar:         11 | acc:        100 | sp:       8094
  DEBUG   datapath:output        hello worl <- d
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        340 | ip:         18 | dr        100 |ar:         11 | acc:        100 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        344 | ip:         19 | dr          0 |ar:         11 | acc:        100 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        348 | ip:         20 | dr         24 |ar:         11 | acc:        100 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        353 | ip:         21 | dr         11 |ar:         11 | acc:         11 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        356 | ip:         22 | dr         11 |ar:         11 | acc:         12 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        359 | ip:         23 | dr         11 |ar:         11 | acc:         12 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        363 | ip:         16 | dr         16 |ar:         11 | acc:         12 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        369 | ip:         17 | dr         33 |ar:         12 | acc:         33 | sp:       8094
  DEBUG   datapath:output        hello world <- !
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        372 | ip:         18 | dr         33 |ar:         12 | acc:         33 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        376 | ip:         19 | dr          0 |ar:         12 | acc:         33 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        380 | ip:         20 | dr         24 |ar:         12 | acc:         33 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.POP | tick:        385 | ip:         21 | dr         12 |ar:         12 | acc:         12 | sp:       8095
  INFO    controlunit:microcode_handler execute_command      Opcode.INC | tick:        388 | ip:         22 | dr         12 |ar:         12 | acc:         13 | sp:       8095
  INFO    controlunit:microcode_handler execute_command     Opcode.PUSH | tick:        391 | ip:         23 | dr         12 |ar:         12 | acc:         13 | sp:       8094
  INFO    controlunit:microcode_handler execute_command     Opcode.JUMP | tick:        395 | ip:         16 | dr         16 |ar:         12 | acc:         13 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.LD | tick:        401 | ip:         17 | dr          0 |ar:         13 | acc:          0 | sp:       8094
  INFO    controlunit:microcode_handler execute_command    Opcode.PRINT | tick:        404 | ip:         18 | dr          0 |ar:         13 | acc:          0 | sp:       8094
  INFO    controlunit:microcode_handler execute_command      Opcode.CMP | tick:        408 | ip:         19 | dr          0 |ar:         13 | acc:          0 | sp:       8094
  INFO    controlunit:microcode_handler execute_command       Opcode.JE | tick:        413 | ip:         24 | dr         24 |ar:         13 | acc:          0 | sp:       8094
  DEBUG   datapath:output_the_buffer output: hello world!
  INFO    processor:simulation    Simulation stop
```

```text  
| ФИО                    | алг             | LoC | code байт | code инстр. | инстр.   | такт.   | вариант                                                                     |
| Бугаев Сергей Юрьевич  | hello_world     | 1   | -         | 24          | 117      | 352     | alg | acc | neum | mc | tick | struct | stream | port | cstr | prob1 | 8bit |
| Бугаев Сергей Юрьевич  | cat             | 7   | -         | 37          | 203      | 699     | alg | acc | neum | mc | tick | struct | stream | port | cstr | prob1 | 8bit |
| Бугаев Сергей Юрьевич  | hello_user      | 11  | -         | 100         | 466      | 1509    | alg | acc | neum | mc | tick | struct | stream | port | cstr | prob1 | 8bit |
| Бугаев Сергей Юрьевич  | prob1           | 14  | -         | 53          | 28523    | 127049  | alg | acc | neum | mc | tick | struct | stream | port | cstr | prob1 | 8bit |
```

> где:
>
> алг. -- название алгоритма (hello, cat, или как в варианте)
>
> прог. LoC -- кол-во строк кода в реализации алгоритма
>
> code байт -- кол-во байт в машинном коде (если бинарное представление)
>
> code инстр. -- кол-во инструкций в машинном коде
>
> инстр. -- кол-во инструкций, выполненных при работе алгоритма
>
> такт. -- кол-во тактов, которое заняла работа алгоритма
