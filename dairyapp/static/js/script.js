class Api {
    async getTypes() {
        const response = await fetch(`${BASE_URL}/meta/types`);
        const body = await response.json();
        if (!response.ok) {
            console.log(body);
        } else {
            return body;
        }
    };
    async getQuest() {
        const response = await fetch(`${BASE_URL}/quest/${QUEST_ID}`);
        const body = await response.json();
        if (!response.ok) {
            console.log(body);
        } else {
            return body;
        };
    };
    async putQuest(items) {
        const response = await fetch(`${BASE_URL}/quest/${QUEST_ID}`, {
            method: "PUT",
            body: JSON.stringify(items),
            headers: {
                "Content-Type": "application/json"
            }
        });
        const body = await response.json()
        if (!response.ok) {
            console.log(body);
        } 
    };
};

const API = new Api();


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
        this.removeButton.textContent = "Remove";
        this.removeButton.addEventListener("click", () => {
            this.item.remove();
        });

        this.item = document.createElement("div");
        this.item.classList.add("item-container__item");
        this.item.append(this.textarea, this.select, this.removeButton);
        
        document.getElementById(containerId).append(this.item);
        return this.item;
    };
};


class Init {
    constructor(types) {
        // const types = types
        // this.types = types;
        this.itemsMap = [
            ["done", "add-done", "done-container", types.done],
            ["errors", "add-error", "error-container", types.errors],
            ["problems", "add-problem", "problem-container", types.problems],
            ["knowledge", "add-knowledge", "knowledge-container", types.knowledge],
        ];
    };
    initView() {
        this.itemsMap.forEach(([_, buttonId, containerId, types]) => {
            document.getElementById(buttonId).addEventListener("click", () => {
                new Item(containerId, types);
            });
        });

        document.getElementById("save-quest").addEventListener("click", async () => {
            const body = {
                theme_description: document.getElementById("theme").value,
                done: [],
                errors: [],
                problems: [],
                knowledge: [],
            };
            
            this.itemsMap.forEach(([key, _, containerId, __]) => {
                for (const item of document.getElementById(containerId).getElementsByTagName("div")) {
                    body[key].push({
                        text: item.getElementsByTagName("textarea")[0].value,
                        type: item.getElementsByTagName("select")[0].value
                    });
                };
            });
            await API.putQuest(body);
            document.location.href = REDIRECT_URL;
        });
    };

    async initItems() {
        const itemsData = await API.getQuest();
        this.itemsMap.forEach(([key, _, containerId, types]) => {
            itemsData[key].forEach(itemData => {
                new Item(containerId, types, itemData.text, itemData.type);
            });
        });
    };
};


document.addEventListener("DOMContentLoaded", async () => {
    const types = await API.getTypes();
    const init = new Init(types)
    init.initView();
    init.initItems();
});