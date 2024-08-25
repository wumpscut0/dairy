const QUEST_DATA = JSON.parse(document.getElementById("quest_data").textContent);

async function putQuest(items) {
    const response = await fetch(ENDPOINT, {
        method: "PUT",
        body: JSON.stringify(items),
        headers: {
            "Content-Type": "application/json"
        }
    });
    if (response.status === 400) {
        alert("Incorrect input");
        return false;
    }; 
    if (!response.ok) {
        alert("something broken");
        return false;
    }
    return true;
};


class Task {
    static containerId = "task-container";
    static checkboxlabelId = "task-ckeckbox-label"
    constructor(taskId, currentText, selectedType, status) {
        this.type = document.createElement("h4");
        this.type.textContent = selectedType;

        this.note = document.createElement("p");
        this.note.textContent = currentText;

        this.checkboxlabel = document.createElement("label");
        this.checkboxlabel.textContent = "Done";
        this.checkboxlabel.for = `task-${taskId}`;
        this.checkbox = document.createElement("input");
        this.checkbox.id = `task-${taskId}`
        this.checkbox.type = "checkbox";
        this.checkbox.checked = !!parseInt(status);

        this.task = document.createElement("div");
        this.task.id = taskId;
        this.task.classList.add("item-container__item");
        this.task.append(this.type, this.note, this.checkboxlabel, this.checkbox);
        
        document.getElementById(Task.containerId).append(this.task);
    };
};


class Item { 
    constructor(containerId, types, currentText="", selectedType=undefined) {
        this.textarea = document.createElement("textarea");
        this.textarea.textContent = currentText;

        this.select = document.createElement("select");
        for (const type in types) {
            const option = document.createElement("option");
            option.textContent = types[type];
            option.value = type;
            this.select.append(option);
        };
        this.select.value = selectedType;

        this.removeButton = document.createElement("button");
        this.removeButton.textContent = "remove";
        this.removeButton.addEventListener("click", () => {
            this.item.remove();
        });

        this.item = document.createElement("div");
        this.item.classList.add("item-container__item");
        this.item.append(this.textarea, this.select, this.removeButton);
        
        document.getElementById(containerId).append(this.item);
    };
};


class Init {
    itemsMap = [
        ["errors", "add-error", "error-container", QUEST_DATA.types.errors],
        ["problems", "add-problem", "problem-container", QUEST_DATA.types.problems],
        ["knowledge", "add-knowledge", "knowledge-container", QUEST_DATA.types.knowledge],
    ];

    constructor() {
        this.initTasks();
        this.initItems();
        this.initListeners();
    };

    initTasks() {
        QUEST_DATA.tasks.forEach(taskData => {
            new Task(taskData.id, taskData.text, QUEST_DATA.types.tasks[taskData.type], taskData.status)
        });
    };

    initItems() {
        this.itemsMap.forEach(([key, _, containerId, types]) => {
            QUEST_DATA[key].forEach(itemData => {
                new Item(containerId, types, itemData.text, itemData.type);
            });
        });
    };

    initListeners() {
        // Event: create empty item
        this.itemsMap.forEach(([_, buttonId, containerId, types]) => {
            document.getElementById(buttonId).addEventListener("click", () => {
                new Item(containerId, types);
            });
        });

        document.getElementById("save-quest").addEventListener("click", async () => {
            const body = {
                tasks: [],
                errors: [],
                problems: [],
                knowledge: [],
            };
            
            this.itemsMap.forEach(([key, _, containerId, __]) => {
                Array.from(document.getElementById(containerId).getElementsByTagName("div")).forEach(item => {
                    body[key].push({
                        text: item.getElementsByTagName("textarea")[0].value,
                        type: item.getElementsByTagName("select")[0].value
                    });
                });
            });
            Array.from(document.getElementById(Task.containerId).getElementsByTagName("div")).forEach((task, index) => {
                console.log(task.getElementsByTagName("input")[0].value);
                body.tasks.push({
                    id: task.id,
                    text: QUEST_DATA.tasks[index].text,
                    status: task.getElementsByTagName("input")[0].checked ? 1 : 0,
                    type: QUEST_DATA.tasks[index].type
                });
            });
            if (await putQuest(body)) {
                document.location.href = REDIRECT_URL;
            };
        });
    };
};


document.addEventListener("DOMContentLoaded", () => {
    new Init();
});