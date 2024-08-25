const TASKS_TYPES = JSON.parse(document.getElementById("tasks_types").textContent);

async function createQuest(quest) {
    const response = await fetch(ENDPOINT, {
        method: "POST",
        body: JSON.stringify(quest),
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
    constructor() {
        this.textarea = document.createElement("textarea");

        this.types = document.createElement("select");
        this.types.value = "Задача";
        for (const type in TASKS_TYPES) {
            const option = document.createElement("option");
            option.textContent = TASKS_TYPES[type];
            option.value = type;
            this.types.append(option);
        };

        this.removeButton = document.createElement("button");
        this.removeButton.textContent = "remove";
        this.removeButton.addEventListener("click", () => {
            this.task.remove();
        });

        this.task = document.createElement("div");
        this.task.classList.add("item-container__item");
        this.task.append(this.textarea, this.types, this.removeButton);
        
        document.getElementById(Task.containerId).append(this.task);
    };
};


class Init {
    constructor() {
        this.initListeners();
    };

    initListeners() {
        // Event: create empty task
        document.getElementById("add-task").addEventListener("click", () => {
            new Task();
        });

        
        document.getElementById("create-quest").addEventListener("click", async () => {
            const body = {
                theme: document.getElementById("theme").value,
                origin: document.getElementById("origin").value,
                tasks: []
            };
            Array.from(document.getElementById(Task.containerId).getElementsByTagName("div")).forEach(task => {
                body.tasks.push({
                    text: task.getElementsByTagName("textarea")[0].value,
                    type: task.getElementsByTagName("select")[0].value
                });
            });

            if (await createQuest(body)) {
                document.location.href = REDIRECT_URL;
            };
        });
    };
};


document.addEventListener("DOMContentLoaded", async () => {
    new Init();
});