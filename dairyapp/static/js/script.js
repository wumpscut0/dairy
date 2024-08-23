class Api {
    baseUrl = "http://localhost:8000/api";
    async getErrorTypes() {
        const response = await fetch(`${this.baseUrl}/meta/errors`);
        const body = await response.json();
        if (!response.ok) {
            console.log(body);
        } else {
            return body;
        }
    };
    async getQuestItems() {
        const response = await fetch(`${this.baseUrl}/quest/${QUEST_ID}`);
        const body = await response.json();
        if (!response.ok) {
            console.log(body);
        } else {
            return body;
        };
    };
    async putQuest(items) {
        const response = await fetch(`${this.baseUrl}/quest/${QUEST_ID}`, {
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
    constructor(containerId, itemId, text="", selectValue=undefined, errorTypes=undefined) {
        this.errorTypes = errorTypes;

        this.itemsContainer = document.getElementById(containerId);
        
        this.itemWrapper = document.createElement("div");
        this.itemWrapper.value = itemId;
        
        this.textarea = document.createElement("textarea");
        this.textarea.textContent = text;

        this.removeButton = document.createElement("button");
        this.removeButton.textContent = "Remove";
        this.removeButton.addEventListener("click", () => {
            this.itemWrapper.innerHTML = '';
            this.itemWrapper.remove();
        });

        if (containerId === "error-container") {
            this.select = document.createElement("select");
            for (const errorType in this.errorTypes) {
                const option = document.createElement("option");
                option.textContent = this.errorTypes[errorType];
                option.value = errorType;
                this.select.append(option);
            };
            this.select.value = selectValue;
            this.itemWrapper.append(this.textarea, this.select, this.removeButton);
        } else {
            this.itemWrapper.append(this.textarea, this.removeButton);
        };

        this.itemWrapper.classList.add("item-container__item");
        
        this.itemsContainer.append(this.itemWrapper);
        return this;
    };
};


class Init {
    constructor(errorTypes) {
        this.errorTypes = errorTypes;
    }
    initView() {
        const theme = document.getElementById("theme")
        const addDone = document.getElementById("add-done");
        const addError = document.getElementById("add-error");
        const addProblem = document.getElementById("add-problem");
        const addKnowledge = document.getElementById("add-knowledge");
        const saveQuest = document.getElementById("save-quest");
        
        addDone.addEventListener("click", () => {
            new Item("done-container", this.genid(this.items.done));
        });
        addError.addEventListener("click", () => {
            new Item("error-container", this.genid(this.items.errors), "", undefined, this.errorTypes);
        });
        addProblem.addEventListener("click", () => {
            new Item("problem-container", this.genid(this.items.problems));
        });
        addKnowledge.addEventListener("click", () => {
            new Item("knowledge-container", this.genid(this.items.knowledge));
        });

        saveQuest.addEventListener("click", async (e) => {
            const doneContainer = document.getElementById("done-container");
            const errorContainer = document.getElementById("error-container");
            const problemContainer = document.getElementById("problem-container");
            const knowledgeContainer = document.getElementById("knowledge-container");
            const body = {
                theme_description: theme.value,
                done: [],
                errors: [],
                problems: [],
                knowledge: [],
            };
            
            for (const wrapper of doneContainer.getElementsByTagName("div")) {
                body.done.push({
                    id: wrapper.value,
                    text: wrapper.getElementsByTagName("textarea")[0].value
                });
            };
            for (const wrapper of doneContainer.getElementsByTagName("div")) {
                body.errors.push({
                    id: wrapper.value,
                    text: wrapper.getElementsByTagName("textarea")[0].value,
                    type: wrapper.getElementsByTagName("select")[0].value
                });
            };
            for (const wrapper of doneContainer.getElementsByTagName("div")) {
                body.problems.push({
                    id: wrapper.value,
                    text: wrapper.getElementsByTagName("textarea")[0].value
                });
            };
            for (const wrapper of doneContainer.getElementsByTagName("div")) {
                body.knowledge.push({
                    id: wrapper.value,
                    text: wrapper.getElementsByTagName("textarea")[0].value
                });
            };
            await API.putQuest(body);
            document.location.href = REDIRECT_URL;
        });
    };

    async initItems() {
        this.items = await API.getQuestItems();
        if (this.items.done) {
            for (const done of this.items.done) {
                new Item("done-container", done.id, done.text);
            };
        };
        if (this.items.errors) {
            for (const error of this.items.errors) {
                new Item("error-container", error.id, error.text, error.type, this.errorTypes);
            };
        };
        if (this.items.problems) {
            for (const problem of this.items.problems) {
                new Item("problem-container", problem.id, problem.text);
            };
        };
        if (this.items.knowledge) {
            for (const knowledge of this.items.knowledge) {
                new Item("knowledge-container", knowledge.id, knowledge.text);
            };
        };
    };

    genid(items) {
        console.log(items);
        const ids = [];
        for (const item of items) {
            ids.push(item.id);
        };
        const id = Math.max(ids) + 1;
        items.push(id)
        return id
    };
};


document.addEventListener("DOMContentLoaded", async () => {
    const errorTypes = await API.getErrorTypes();
    const init = new Init(errorTypes)
    init.initView();
    init.initItems();
});