import "frida-java-menu";

function setupTheme() {
  Menu.theme = Menu.Theme.LGL;
  Menu.theme.bgColor = "#101a20";
  Menu.theme.primaryTextColor = "#00ffc8";
  Menu.theme.menuHeight = 320;
}

export { setupTheme };