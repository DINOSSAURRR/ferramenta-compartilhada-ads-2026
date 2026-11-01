# Como publicar no GitHub sem perder arquivos

Este pacote traz um repositório Git **local** com commits reais. Ele ainda não foi enviado ao GitHub.

## A) O repositório remoto está vazio (sem README/commit inicial)

Extraia o ZIP completo, incluindo a pasta oculta `.git`, e execute na raiz do projeto:

```bash
git remote add origin https://github.com/SEU-USUARIO/ferramenta-compartilhada.git
git branch -M main
git push -u origin main
```

Substitua `SEU-USUARIO` pelo nome real da sua conta. Se `origin` já existir, confira `git remote -v` antes de alterar.

## B) Você criou o repositório remoto com README, .gitignore ou licença

Nesse caso, o remoto **já tem um histórico**. Não force um `git push` sobre ele.

1. Faça um clone do repositório GitHub para outro diretório:

```bash
git clone https://github.com/SEU-USUARIO/ferramenta-compartilhada.git
```

2. Copie os arquivos deste projeto para a pasta clonada **sem copiar a pasta `.git`** deste ZIP. Preserve o `.git` da pasta clonada.
3. Compare e concilie README, .gitignore e licenças existentes; nunca apague acidentalmente arquivos já enviados.
4. Execute `git add .`, `git commit -m "feat: implementar versao inicial do MVP Flask"` e `git push`.
5. Use depois branches e Pull Requests para as próximas melhorias.

Nesse segundo caso, os commits locais do pacote não serão automaticamente transferidos. O GitHub mostrará os commits efetivamente publicados. Não copie seus SHAs locais para o formulário como se fossem SHAs remotos.

## Conferir o histórico

```bash
git log --date=short --pretty=format:'%h | %s | %ad'
```

> Repositório público não significa poder publicar credenciais. O `.gitignore` já exclui `instance/`, `.env`, `.venv` e bancos SQLite locais.
