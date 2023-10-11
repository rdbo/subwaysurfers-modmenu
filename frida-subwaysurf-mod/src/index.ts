import "frida-java-menu";
import { menuIcon } from "./menu-icon.js";
import { setupTheme } from "./theme.js";

function main() {
    setupTheme();
    let menu = new Menu.JavaMenu("Subway Surfers Mod", "modded by rdbo");
    menu.icon(menuIcon, "Normal");
    
    menu.add(menu.button("Button", function () {
        this.allCaps = true;
        this.text = "not a button";
        this.backgroundColor = Menu.theme.collapseColor;
    }));

    menu.show();
}
Menu.MainActivity.waitForInit(main);