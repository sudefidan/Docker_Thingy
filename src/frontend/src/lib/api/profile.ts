import { goto } from '$app/navigation';

// helper function to get the access token
function getToken(): string {
    const token = localStorage.getItem('access_token');
    if (!token) {
        goto('/login');
        throw new Error('Not authenticated');
    }
    return token;
}

export interface UserProfile {
    profile_picture: string;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    social_type: string[];
    social_username: string[];
    about: string;
    interests: string[];
    address: string;
    program: string;
    uni_year: string;
}

export async function fetchUserProfile(): Promise<UserProfile> {
    const token = localStorage.getItem('access_token');
    if (!token) {
        goto('/login');
        throw new Error('Not authenticated');
    }

    const response = await fetch('http://localhost:8000/api/user-profile/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch profile');
    }

    const data = await response.json();
    return {
        ...data,
        social_type: data.social_type || [],
        social_username: data.social_username || []
    };
}

export async function updateProfile(profile: {
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    address: string;
    program: string;
    year: string;
}): Promise<void> {
    try {
        const response = await fetch('http://localhost:8000/api/update-profile/', {
        method: 'PUT',
        headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(profile)
    });

    if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update profile');
        }

        // profile updated successfully
        return;
    } catch (error) {
        console.error('Error updating profile:', error);
        throw error;
    }
}

export async function updateProfilePicture(base64Image: string): Promise<void> {
    const token = localStorage.getItem('access_token');
    if (!token) {
        goto('/login');
        throw new Error('Not authenticated');
    }

    const response = await fetch('http://localhost:8000/api/upload-profile-picture/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            profile_picture: base64Image
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update profile picture');
    }

    const data = await response.json();
    return data;
}

// handles password change requests
export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
    const response = await fetch('http://localhost:8000/api/change-password/', {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword
        })
    });

    if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to change password');
        }

        // password changed successfully
        return;
    } catch (error) {
        console.error('Error changing password:', error);
        throw error;
    }
}

// Social media icons
export const socialMediaIcons = {
    Instagram: `<svg width="25" height="27" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 525 480"><rect width="512" height="512" rx="15%" id="b"/><use fill="url(#a)" xlink:href="#b"/><use fill="url(#c)" xlink:href="#b"/><radialGradient id="a" cx=".4" cy="1" r="1"><stop offset=".1" stop-color="#fd5"/><stop offset=".5" stop-color="#ff543e"/><stop offset="1" stop-color="#c837ab"/></radialGradient><linearGradient id="c" x2=".2" y2="1"><stop offset=".1" stop-color="#3771c8"/><stop offset=".5" stop-color="#60f" stop-opacity="0"/></linearGradient><g fill="none" stroke="#fff" stroke-width="30"><rect width="308" height="308" x="102" y="102" rx="81"/><circle cx="256" cy="256" r="72"/><circle cx="347" cy="165" r="6"/></g></svg>`,
    LinkedIn: `<svg width="24" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"> <rect x="2" y="2" width="28" height="28" rx="14" fill="#1275B1"/> <path d="M12.6186 9.69215C12.6186 10.6267 11.8085 11.3843 10.8093 11.3843C9.81004 11.3843 9 10.6267 9 9.69215C9 8.7576 9.81004 8 10.8093 8C11.8085 8 12.6186 8.7576 12.6186 9.69215Z" fill="white"/> <path d="M9.24742 12.6281H12.3402V22H9.24742V12.6281Z" fill="white"/> <path d="M17.3196 12.6281H14.2268V22H17.3196C17.3196 22 17.3196 19.0496 17.3196 17.2049C17.3196 16.0976 17.6977 14.9855 19.2062 14.9855C20.911 14.9855 20.9008 16.4345 20.8928 17.5571C20.8824 19.0244 20.9072 20.5219 20.9072 22H24V17.0537C23.9738 13.8954 23.1508 12.4401 20.4433 12.4401C18.8354 12.4401 17.8387 13.1701 17.3196 13.8305V12.6281Z" fill="white"/> </svg>`,
    X: `<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" viewBox="0 0 16 15"> <path d="M12.6.75h2.454l-5.36 6.142L16 15.25h-4.937l-3.867-5.07-4.425 5.07H.316l5.733-6.57L0 .75h5.063l3.495 4.633L12.601.75Zm-.86 13.028h1.36L4.323 2.145H2.865z"/></svg>`,
    Facebook: `<svg width="25" height="25" viewBox="0 0 16.5 16" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#1877F2" d="M15 8a7 7 0 00-7-7 7 7 0 00-1.094 13.915v-4.892H5.13V8h1.777V6.458c0-1.754 1.045-2.724 2.644-2.724.766 0 1.567.137 1.567.137v1.723h-.883c-.87 0-1.14.54-1.14 1.093V8h1.941l-.31 2.023H9.094v4.892A7.001 7.001 0 0015 8z"/><path fill="#ffffff" d="M10.725 10.023L11.035 8H9.094V6.687c0-.553.27-1.093 1.14-1.093h.883V3.87s-.801-.137-1.567-.137c-1.6 0-2.644.97-2.644 2.724V8H5.13v2.023h1.777v4.892a7.037 7.037 0 002.188 0v-4.892h1.63z"/></svg>`,
    Snapchat: `<svg width="30" height="25" viewBox="0 0 32 30" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="16" cy="16" r="14" fill="#FFFA37"/><path fill-rule="evenodd" clip-rule="evenodd" d="M21.0255 8.18551C20.0601 6.96879 18.4673 6 16.0118 6C13.9091 6.02071 9.70378 7.18445 9.70378 11.6738C9.70378 12.3294 9.75568 13.2075 9.80103 13.8541C9.74758 13.8386 9.68188 13.8095 9.57775 13.7596L9.56328 13.7527C9.37915 13.6643 9.09918 13.5298 8.7098 13.5298C8.31645 13.5298 7.93611 13.6839 7.65375 13.9124C7.37309 14.1394 7.13333 14.4885 7.13333 14.9105C7.13333 15.4384 7.43041 15.7888 7.77778 16.0135C8.08632 16.2131 8.47538 16.3406 8.78337 16.4415L8.81382 16.4514C9.14349 16.5596 9.3851 16.642 9.55169 16.7458C9.68136 16.8267 9.70104 16.8778 9.70348 16.9264C9.70179 16.9333 9.69782 16.9482 9.68919 16.9724C9.67141 17.0224 9.64184 17.0899 9.59862 17.1743C9.5124 17.3427 9.38667 17.5498 9.23711 17.7706C8.93539 18.2161 8.56717 18.673 8.29212 18.9376C8.02082 19.1986 7.57562 19.5229 7.11016 19.7811C6.87933 19.9091 6.6536 20.0152 6.45167 20.0881C6.24322 20.1633 6.09047 20.192 5.99608 20.192C5.92136 20.192 5.85669 20.2073 5.82847 20.2144C5.7888 20.2243 5.74774 20.2374 5.70713 20.2527C5.62657 20.2829 5.53056 20.3283 5.43546 20.3923C5.25377 20.5146 5 20.7612 5 21.1502C5 21.3532 5.04766 21.5251 5.13005 21.6742C5.20217 21.8047 5.29487 21.9038 5.34823 21.9608L5.35615 21.9692L5.37091 21.9851C5.66435 22.3008 6.15008 22.5205 6.62162 22.6712C7.02679 22.8007 7.4798 22.8972 7.92122 22.9551C7.92745 22.9836 7.93397 23.0142 7.9411 23.0478L7.9434 23.0587C7.97119 23.1897 8.008 23.3633 8.06221 23.5234C8.11336 23.6744 8.20599 23.8977 8.39564 24.0568C8.63717 24.2593 8.95308 24.2798 9.1592 24.279C9.38047 24.2781 9.63881 24.2469 9.88394 24.2174L9.90481 24.2149C10.2497 24.1733 10.6106 24.1304 10.9843 24.1304C11.6663 24.1304 12.1035 24.4153 12.7894 24.8837L12.794 24.8869C13.0316 25.0492 13.2976 25.2308 13.6 25.4095C14.6122 26.0076 15.4346 26.0025 15.9007 25.9995C15.9315 25.9993 15.9606 25.9992 15.9882 25.9992C16.0158 25.9992 16.0452 25.9993 16.0761 25.9995C16.543 26.0025 17.3873 26.0079 18.4 25.4095C18.7024 25.2308 18.9684 25.0492 19.2059 24.8869L19.2106 24.8837C19.8965 24.4153 20.3337 24.1304 21.0157 24.1304C21.3894 24.1304 21.7503 24.1733 22.0952 24.2149L22.1161 24.2174C22.3612 24.2469 22.6195 24.2781 22.8408 24.279C23.0469 24.2798 23.3628 24.2593 23.6044 24.0568C23.794 23.8977 23.8866 23.6744 23.9378 23.5234C23.992 23.3634 24.0288 23.1898 24.0566 23.0587L24.0589 23.0478C24.066 23.0142 24.0725 22.9836 24.0788 22.9551C24.5202 22.8972 24.9732 22.8007 25.3784 22.6712C25.8499 22.5205 26.3357 22.3007 26.6291 21.985L26.6439 21.9692L26.6517 21.9608C26.7051 21.9038 26.7978 21.8047 26.8699 21.6742C26.9523 21.5251 27 21.3532 27 21.1502C27 20.7612 26.7462 20.5146 26.5645 20.3923C26.4694 20.3283 26.3734 20.2829 26.2929 20.2527C26.2523 20.2374 26.2112 20.2243 26.1715 20.2144C26.1433 20.2073 26.0786 20.192 26.0039 20.192C25.9095 20.192 25.7568 20.1633 25.5483 20.0881C25.3464 20.0152 25.1207 19.9091 24.8898 19.7811C24.4244 19.5229 23.9792 19.1986 23.7079 18.9376C23.4328 18.673 23.0646 18.2161 22.7629 17.7706C22.6133 17.5498 22.4876 17.3427 22.4014 17.1743C22.3582 17.0899 22.3286 17.0224 22.3108 16.9724C22.3022 16.9482 22.2982 16.9333 22.2965 16.9264C22.299 16.8778 22.3186 16.8267 22.4483 16.7458C22.6149 16.642 22.8565 16.5596 23.1862 16.4514L23.2166 16.4415C23.5246 16.3406 23.9137 16.2131 24.2222 16.0135C24.5696 15.7888 24.8667 15.4384 24.8667 14.9105C24.8667 14.4885 24.6269 14.1394 24.3462 13.9124C24.0639 13.6839 23.6835 13.5298 23.2902 13.5298C22.9008 13.5298 22.6209 13.6643 22.4367 13.7527L22.4223 13.7596C22.3181 13.8095 22.2524 13.8386 22.199 13.8541C22.2443 13.2075 22.2962 12.3294 22.2962 11.6738C22.2962 10.7837 21.9726 9.37904 21.0255 8.18551ZM11.7832 8.77274C10.9822 9.77549 10.7077 10.9662 10.7077 11.6738C10.7077 12.3299 10.7633 13.2413 10.8102 13.8949C10.8258 14.1119 10.7813 14.365 10.5917 14.5658C10.3998 14.7691 10.1388 14.8351 9.90561 14.8351C9.56889 14.8351 9.3128 14.7119 9.14898 14.6331L9.12996 14.624C8.94718 14.5363 8.85108 14.4956 8.7098 14.4956C8.58128 14.4956 8.42437 14.5508 8.29994 14.6515C8.17382 14.7535 8.13725 14.8534 8.13725 14.9105C8.13725 15.0269 8.18018 15.1101 8.33794 15.2121C8.52427 15.3326 8.78976 15.4232 9.13779 15.5374L9.16809 15.5473C9.45712 15.642 9.81511 15.7593 10.0976 15.9354C10.4147 16.133 10.7077 16.4507 10.7077 16.9401C10.7077 17.0684 10.6722 17.1919 10.6389 17.2854C10.6028 17.3869 10.554 17.4941 10.4992 17.601C10.3896 17.8152 10.2413 18.0571 10.0783 18.2978C9.75483 18.7754 9.3437 19.2918 9.002 19.6205C8.65655 19.9528 8.13703 20.3263 7.61159 20.6178C7.34696 20.7645 7.07068 20.8961 6.80428 20.9923C6.56581 21.0783 6.3088 21.1457 6.06224 21.1563C6.0561 21.1589 6.04931 21.162 6.0422 21.1655C6.03083 21.1713 6.0202 21.1774 6.01092 21.1837L6.00618 21.187C6.00711 21.1936 6.00817 21.1985 6.00906 21.202C6.01103 21.2097 6.01337 21.2152 6.01652 21.2209C6.02619 21.2384 6.04143 21.2579 6.1031 21.324L6.11928 21.3413C6.23038 21.4609 6.50416 21.616 6.93815 21.7547C7.35148 21.8868 7.84023 21.9822 8.30201 22.026C8.53305 22.0479 8.66621 22.1923 8.72257 22.2701C8.78059 22.3501 8.81377 22.4347 8.83316 22.4908C8.87067 22.5994 8.899 22.7332 8.92135 22.8387L8.92474 22.8547C8.95525 22.9985 8.98194 23.1215 9.01675 23.2242C9.02905 23.2606 9.0404 23.2882 9.05017 23.3085C9.0722 23.3111 9.10599 23.3135 9.15493 23.3133C9.36726 23.3124 9.57984 23.2808 9.79022 23.2554C10.1268 23.2148 10.5433 23.1646 10.9843 23.1646C12.0071 23.1646 12.682 23.6258 13.334 24.0713L13.3706 24.0963C13.6118 24.261 13.8536 24.4259 14.1255 24.5866C14.8917 25.0394 15.4747 25.0361 15.9007 25.0337C15.9306 25.0336 15.9598 25.0334 15.9882 25.0334C16.0164 25.0334 16.0454 25.0336 16.0753 25.0337C16.5059 25.036 17.1085 25.0393 17.8745 24.5866C18.1464 24.4259 18.3882 24.261 18.6294 24.0963L18.666 24.0713C19.318 23.6258 19.9929 23.1646 21.0157 23.1646C21.4567 23.1646 21.8732 23.2148 22.2098 23.2554L22.2199 23.2566C22.4921 23.2894 22.6913 23.3126 22.8451 23.3133C22.894 23.3135 22.9278 23.3111 22.9498 23.3085C22.9596 23.2882 22.9709 23.2606 22.9833 23.2242C23.0181 23.1215 23.0447 22.9985 23.0753 22.8547L23.0787 22.8387C23.101 22.7331 23.1293 22.5994 23.1668 22.4908C23.1862 22.4347 23.2194 22.3501 23.2774 22.2701C23.3338 22.1923 23.467 22.0479 23.698 22.026C24.1598 21.9822 24.6485 21.8868 25.0618 21.7547C25.4958 21.616 25.7696 21.4609 25.8807 21.3414L25.8969 21.324C25.9585 21.2579 25.9738 21.2384 25.9835 21.2209C25.9866 21.2152 25.989 21.2097 25.9909 21.202C25.9918 21.1985 25.9929 21.1936 25.9938 21.187L25.9891 21.1837C25.9798 21.1774 25.9692 21.1713 25.9578 21.1655C25.9507 21.1619 25.9439 21.1589 25.9378 21.1563C25.6912 21.1457 25.4342 21.0783 25.1957 20.9923C24.9293 20.8961 24.653 20.7645 24.3884 20.6178C23.863 20.3263 23.3435 19.9528 22.998 19.6205C22.6563 19.2918 22.2452 18.7754 21.9217 18.2978C21.7587 18.0571 21.6104 17.8152 21.5008 17.601C21.446 17.4941 21.3972 17.3869 21.3611 17.2854C21.3278 17.1919 21.2923 17.0684 21.2923 16.9401C21.2923 16.4507 21.5853 16.133 21.9024 15.9354C22.1849 15.7593 22.5429 15.642 22.8319 15.5473L22.8622 15.5374C23.2102 15.4232 23.4757 15.3326 23.6621 15.2121C23.8198 15.1101 23.8627 15.0269 23.8627 14.9105C23.8627 14.8534 23.8262 14.7535 23.7001 14.6515C23.5756 14.5508 23.4187 14.4956 23.2902 14.4956C23.1489 14.4956 23.0528 14.5363 22.87 14.624L22.851 14.6331C22.6872 14.7119 22.4311 14.8351 22.0944 14.8351C21.8612 14.8351 21.6002 14.7691 21.4083 14.5658C21.2187 14.365 21.1742 14.1119 21.1898 13.8949C21.2367 13.2413 21.2923 12.3299 21.2923 11.6738C21.2923 10.9643 21.0227 9.77352 20.2275 8.77149C19.4508 7.79264 18.1523 6.96575 16.0118 6.96575C13.871 6.96575 12.566 7.79288 11.7832 8.77274Z" fill="#000000"/><path fill-rule="evenodd" clip-rule="evenodd" d="M11.7829 8.77281C10.9818 9.77556 10.7074 10.9662 10.7074 11.6738C10.7074 12.3299 10.763 13.2414 10.8099 13.895C10.8254 14.112 10.7809 14.365 10.5914 14.5659C10.3995 14.7692 10.1385 14.8352 9.90529 14.8352C9.56858 14.8352 9.31249 14.712 9.14866 14.6332L9.12964 14.624C8.94686 14.5364 8.85077 14.4956 8.70949 14.4956C8.58097 14.4956 8.42405 14.5509 8.29963 14.6515C8.1735 14.7536 8.13694 14.8535 8.13694 14.9106C8.13694 15.027 8.17987 15.1101 8.33763 15.2122C8.52395 15.3327 8.78944 15.4233 9.13748 15.5374L9.16778 15.5474C9.4568 15.6421 9.81479 15.7593 10.0973 15.9354C10.4144 16.1331 10.7074 16.4508 10.7074 16.9402C10.7074 17.0685 10.6719 17.192 10.6386 17.2855C10.6025 17.387 10.5536 17.4942 10.4989 17.6011C10.3893 17.8153 10.241 18.0572 10.0779 18.2979C9.75451 18.7754 9.34339 19.2918 9.00168 19.6206C8.65623 19.9529 8.13672 20.3264 7.61127 20.6178C7.34664 20.7646 7.07037 20.8962 6.80396 20.9923C6.56549 21.0784 6.30848 21.1458 6.06192 21.1563C6.05578 21.1589 6.04899 21.162 6.04188 21.1656C6.03051 21.1713 6.01988 21.1775 6.01061 21.1837L6.00586 21.187C6.00679 21.1937 6.00785 21.1986 6.00874 21.2021C6.01071 21.2098 6.01305 21.2153 6.01621 21.221C6.02587 21.2385 6.04112 21.258 6.10279 21.3241L6.11897 21.3414C6.23006 21.4609 6.50385 21.616 6.93783 21.7548C7.35116 21.8869 7.83992 21.9823 8.30169 22.0261C8.53273 22.048 8.6659 22.1924 8.72226 22.2701C8.78027 22.3502 8.81345 22.4348 8.83284 22.4909C8.87035 22.5995 8.89868 22.7332 8.92103 22.8387L8.92443 22.8548C8.95494 22.9986 8.98162 23.1215 9.01643 23.2243C9.02873 23.2606 9.04009 23.2883 9.04986 23.3086C9.07189 23.3111 9.10567 23.3135 9.15461 23.3133C9.36694 23.3125 9.57952 23.2808 9.7899 23.2555C10.1265 23.2149 10.543 23.1647 10.984 23.1647C12.0068 23.1647 12.6817 23.6259 13.3336 24.0713L13.3702 24.0963C13.6115 24.2611 13.8533 24.426 14.1252 24.5867C14.8914 25.0395 15.4744 25.0362 15.9003 25.0338C15.9303 25.0336 15.9595 25.0335 15.9879 25.0335C16.0161 25.0335 16.0451 25.0336 16.075 25.0338C16.5056 25.0361 17.1081 25.0394 17.8742 24.5867C18.1461 24.426 18.3879 24.2611 18.6291 24.0963L18.6657 24.0713C19.3177 23.6259 19.9926 23.1647 21.0154 23.1647C21.4564 23.1647 21.8729 23.2149 22.2095 23.2555L22.2196 23.2567C22.4918 23.2895 22.691 23.3127 22.8448 23.3133C22.8937 23.3135 22.9275 23.3111 22.9495 23.3086C22.9593 23.2883 22.9706 23.2606 22.9829 23.2243C23.0177 23.1215 23.0444 22.9986 23.0749 22.8548L23.0783 22.8387C23.1007 22.7332 23.129 22.5995 23.1665 22.4909C23.1859 22.4347 23.2191 22.3502 23.2771 22.2701C23.3335 22.1923 23.4666 22.048 23.6977 22.0261C24.1595 21.9823 24.6482 21.8869 25.0615 21.7548C25.4955 21.616 25.7693 21.461 25.8804 21.3414L25.8966 21.3241C25.9582 21.258 25.9735 21.2385 25.9832 21.221C25.9863 21.2153 25.9887 21.2098 25.9906 21.2021C25.9915 21.1986 25.9926 21.1937 25.9935 21.187L25.9888 21.1837C25.9795 21.1775 25.9689 21.1713 25.9575 21.1656C25.9504 21.162 25.9436 21.1589 25.9374 21.1563C25.6909 21.1458 25.4339 21.0784 25.1954 20.9923C24.929 20.8962 24.6527 20.7646 24.3881 20.6178C23.8626 20.3264 23.3431 19.9529 22.9977 19.6206C22.656 19.2918 22.2449 18.7754 21.9214 18.2979C21.7584 18.0572 21.6101 17.8153 21.5004 17.6011C21.4457 17.4942 21.3969 17.387 21.3607 17.2855C21.3275 17.192 21.292 17.0685 21.292 16.9402C21.292 16.4508 21.585 16.1331 21.9021 15.9354C22.1846 15.7593 22.5426 15.6421 22.8316 15.5474L22.8619 15.5374C23.2099 15.4233 23.4754 15.3327 23.6617 15.2122C23.8195 15.1101 23.8624 15.027 23.8624 14.9106C23.8624 14.8535 23.8259 14.7536 23.6997 14.6515C23.5753 14.5509 23.4184 14.4956 23.2899 14.4956C23.1486 14.4956 23.0525 14.5364 22.8697 14.624L22.8507 14.6332C22.6869 14.712 22.4308 14.8352 22.0941 14.8352C21.8609 14.8352 21.5999 14.7692 21.408 14.5659C21.2184 14.365 21.1739 14.112 21.1895 13.895C21.2364 13.2414 21.292 12.3299 21.292 11.6738C21.292 10.9644 21.0224 9.7736 20.2272 8.77157C19.4505 7.79271 18.152 6.96582 16.0114 6.96582C13.8706 6.96582 12.5657 7.79296 11.7829 8.77281Z" fill="white"/></svg>`,
    TikTok: `<svg width="25" height="25" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 510 480"><defs><path id="t" d="M219 200a117 117 0 1 0 101 115v-128a150 150 0 0 0 88 28v-63a88 88 0 0 1-88-88h-64v252a54 54 0 1 1-37-51z" style="mix-blend-mode:multiply"/></defs><use href="#t" fill="#f05" x="18" y="15"/><use href="#t" fill="#0ee"/></svg>`,
    Discord: `<svg width="26" height="27" viewBox="2 0 480 460" fill="#5865f2" xmlns="http://www.w3.org/2000/svg"><path d="m386 137c-24-11-49.5-19-76.3-23.7c-.5 0-1 0-1.2.6c-3.3 5.9-7 13.5-9.5 19.5c-29-4.3-57.5-4.3-85.7 0c-2.6-6.2-6.3-13.7-10-19.5c-.3-.4-.7-.7-1.2-.6c-23 4.6-52.4 13-76 23.7c-.2 0-.4.2-.5.4c-49 73-62 143-55 213c0 .3.2.7.5 1c32 23.6 63 38 93.6 47.3c.5 0 1 0 1.3-.4c7.2-9.8 13.6-20.2 19.2-31.2c.3-.6 0-1.4-.7-1.6c-10-4-20-8.6-29.3-14c-.7-.4-.8-1.5 0-2c2-1.5 4-3 5.8-4.5c.3-.3.8-.3 1.2-.2c61.4 28 128 28 188 0c.4-.2.9-.1 1.2.1c1.9 1.6 3.8 3.1 5.8 4.6c.7.5.6 1.6 0 2c-9.3 5.5-19 10-29.3 14c-.7.3-1 1-.6 1.7c5.6 11 12.1 21.3 19 31c.3.4.8.6 1.3.4c30.6-9.5 61.7-23.8 93.8-47.3c.3-.2.5-.5.5-1c7.8-80.9-13.1-151-55.4-213c0-.2-.3-.4-.5-.4Zm-192 171c-19 0-34-17-34-38c0-21 15-38 34-38c19 0 34 17 34 38c0 21-15 38-34 38zm125 0c-19 0-34-17-34-38c0-21 15-38 34-38c19 0 34 17 34 38c0 21-15 38-34 38z" fill="#5865f2"/></svg>`,
    Steam: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="26" viewBox="0 0 520 510" fill="#ebebeb"><rect width="512" height="512" rx="15%" fill="#231f20"/><path d="m183 280 41 28 27 41 87-62-94-96"/><circle cx="340" cy="190" r="49"/><g fill="none" stroke="#ebebeb"><circle cx="179" cy="352" r="63" stroke-width="19"/><path d="m-18 271 195 81" stroke-width="80" stroke-linecap="round"/><circle cx="340" cy="190" r="81" stroke-width="32"/></g></svg>`,
    YouTube: `<svg width="25" height="25" viewBox="0 0 24 21" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#FF0000" d="M23.498 6.186a2.998 2.998 0 0 0-2.113-2.113C19.69 3.5 12 3.5 12 3.5s-7.69 0-9.385.573a2.998 2.998 0 0 0-2.113 2.113C0 7.881 0 12 0 12s0 4.119.502 5.814a2.998 2.998 0 0 0 2.113 2.113C4.31 20.5 12 20.5 12 20.5s7.69 0 9.385-.573a2.998 2.998 0 0 0 2.113-2.113C24 16.119 24 12 24 12s0-4.119-.502-5.814zM9.75 15.5v-7l6.5 3.5-6.5 3.5z"/></svg>`,
    Pinterest: `<svg width="24" height="27" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 510 510"><rect width="512" height="512" rx="15%" fill="#bd081b"/><path d="m265 65c-104 0-157 75-157 138 0 37 14 71 45 83 5 2 10 0 12-5l3-18c2-6 1-7-2-12-9-11-15-24-15-43 0-56 41-106 108-106 60 0 92 37 92 85 0 64-28 116-70 116-23 0-40-18-34-42 6-27 19-57 19-77 0-18-9-34-30-34-24 0-42 25-42 58 0 20 7 34 7 34l-29 120a249 249 0 0 0 2 86l3-1c2-3 31-37 40-72l16-61c7 15 29 28 53 28 71 0 119-64 119-151 0-66-56-126-140-126z" fill="#fff"/></svg>`,
    Reddit: `<svg width="25" height="25" viewBox="0 40 1030 850" xmlns="http://www.w3.org/2000/svg"><circle cx="512" cy="512" r="512" style="fill:#ff4500"/><path d="M768 516c0-30.9-25.1-56-56-56-15.1 0-28.8 6-38.9 15.7-38.3-27.6-91.1-45.5-149.8-47.5l25.5-120.1 83.4 17.7c1 21.2 18.4 38.1 39.8 38.1 22.1 0 40-17.9 40-40s-17.9-40-40-40c-15.7 0-29.2 9.1-35.7 22.3l-93.1-19.8c-2.6-.6-5.3-.1-7.5 1.4-2.2 1.4-3.8 3.7-4.3 6.3l-28.5 134c-59.6 1.7-113.2 19.5-152 47.5-10.1-9.7-23.7-15.6-38.7-15.6-30.9 0-56 25.1-56 56 0 22.8 13.6 42.3 33.1 51.1-.9 5.6-1.3 11.2-1.3 16.9 0 86.2 100.3 156.1 224.1 156.1S736 670.2 736 584c0-5.7-.5-11.3-1.3-16.8 19.6-8.7 33.3-28.3 33.3-51.2zm-384.1 40c0-22.1 18-40 40-40 22.1 0 40 18 40 40 0 22.1-17.9 40-40 40s-40-17.9-40-40zM607 661.8c-27.3 27.3-79.7 29.4-95 29.4-15.4 0-67.7-2.1-95-29.4-4-4-4-10.6 0-14.7 4-4 10.6-4 14.7 0 17.2 17.2 54 23.3 80.3 23.3 26.3 0 63.1-6.1 80.4-23.3 4.1-4 10.6-4 14.7 0 4 4.1 4 10.6-.1 14.7zm-7-65.8c-22.1 0-40-18-40-40 0-22.1 18-40 40-40 22.1 0 40 18 40 40 0 22.1-18 40-40 40z" style="fill:#fff"/></svg>`,
    GitHub: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="27" viewBox="0 0 532 510"><rect width="512" height="512" rx="15%"	fill="#1B1817"/><path fill="#fff" d="M335 499c14 0 12 17 12 17H165s-2-17 12-17c13 0 16-6 16-12l-1-50c-71 16-86-28-86-28-12-30-28-37-28-37-24-16 1-16 1-16 26 2 40 26 40 26 22 39 59 28 74 22 2-17 9-28 16-35-57-6-116-28-116-126 0-28 10-51 26-69-3-6-11-32 3-67 0 0 21-7 70 26 42-12 86-12 128 0 49-33 70-26 70-26 14 35 6 61 3 67 16 18 26 41 26 69 0 98-60 120-117 126 10 8 18 24 18 48l-1 70c0 6 3 12 16 12z"/></svg>`,
    Twitch: `<svg width="24" height="25" viewBox="0 0 15 12" xmlns="http://www.w3.org/2000/svg"><path fill="#ffffff" d="M13 7.5l-2 2H9l-1.75 1.75V9.5H5V2h8v5.5z"/><g fill="#9146FF"><path d="M4.5 1L2 3.5v9h3V15l2.5-2.5h2L14 8V1H4.5zM13 7.5l-2 2H9l-1.75 1.75V9.5H5V2h8v5.5z"/><path d="M11.5 3.75h-1v3h1v-3zM8.75 3.75h-1v3h1v-3z"/></g></svg>`,
    Spotify: `<svg width="24" height="25" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 496 500"><path fill="#1ed760" d="M248 8C111.1 8 0 119.1 0 256s111.1 248 248 248 248-111.1 248-248S384.9 8 248 8Z"/><path d="M406.6 231.1c-5.2 0-8.4-1.3-12.9-3.9-71.2-42.5-198.5-52.7-280.9-29.7-3.6 1-8.1 2.6-12.9 2.6-13.2 0-23.3-10.3-23.3-23.6 0-13.6 8.4-21.3 17.4-23.9 35.2-10.3 74.6-15.2 117.5-15.2 73 0 149.5 15.2 205.4 47.8 7.8 4.5 12.9 10.7 12.9 22.6 0 13.6-11 23.3-23.2 23.3zm-31 76.2c-5.2 0-8.7-2.3-12.3-4.2-62.5-37-155.7-51.9-238.6-29.4-4.8 1.3-7.4 2.6-11.9 2.6-10.7 0-19.4-8.7-19.4-19.4s5.2-17.8 15.5-20.7c27.8-7.8 56.2-13.6 97.8-13.6 64.9 0 127.6 16.1 177 45.5 8.1 4.8 11.3 11 11.3 19.7-.1 10.8-8.5 19.5-19.4 19.5zm-26.9 65.6c-4.2 0-6.8-1.3-10.7-3.6-62.4-37.6-135-39.2-206.7-24.5-3.9 1-9 2.6-11.9 2.6-9.7 0-15.8-7.7-15.8-15.8 0-10.3 6.1-15.2 13.6-16.8 81.9-18.1 165.6-16.5 237 26.2 6.1 3.9 9.7 7.4 9.7 16.5s-7.1 15.4-15.2 15.4z"/></svg>`,
};

export interface SocialMedia {
    name: string;
    svg: string;
}

export const socialMedias: SocialMedia[] = [
    { name: 'Instagram', svg: socialMediaIcons.Instagram },
    { name: 'LinkedIn', svg: socialMediaIcons.LinkedIn },
    { name: 'X', svg: socialMediaIcons.X },
    { name: 'Facebook', svg: socialMediaIcons.Facebook },
    { name: 'Snapchat', svg: socialMediaIcons.Snapchat },
    { name: 'TikTok', svg: socialMediaIcons.TikTok },
    { name: 'Discord', svg: socialMediaIcons.Discord },
    { name: 'Steam', svg: socialMediaIcons.Steam },
    { name: 'YouTube', svg: socialMediaIcons.YouTube },
    { name: 'Pinterest', svg: socialMediaIcons.Pinterest },
    { name: 'Reddit', svg: socialMediaIcons.Reddit },
    { name: 'GitHub', svg: socialMediaIcons.GitHub },
    { name: "Twitch", svg: socialMediaIcons.Twitch },
    { name: "Spotify", svg: socialMediaIcons.Spotify },
];

export async function updateSocialMedia(socialType: string, socialUsername: string) {
    try {
        const token = getToken();
        const response = await fetch('http://localhost:8000/api/update-social-media/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                social_type: socialType,
                social_username: socialUsername
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update social media');
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating social media:', error);
        throw error;
    }
}

export async function removeSocialMedia(socialType: string): Promise<void> {
    try {
        const response = await fetch('http://localhost:8000/api/update-social-media/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                social_type: socialType
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to remove social media');
        }
    } catch (error) {
        console.error('Error removing social media:', error);
        throw error;
    }
}

// handles about section updates
// sends the new about text to the backend
// returns the updated about section data
export async function updateAbout(about: string): Promise<{ message: string; about: string }> {
    try {
        const response = await fetch('http://localhost:8000/api/update-about/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({ about })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update about section');
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating about section:', error);
        throw error;
    }
}

// Adds a new interest to the user's profile
export async function addInterest(interest: string): Promise<UserProfile> {
  try {
    const response = await fetch('http://localhost:8000/api/user-interests/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ interest })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to add interest');
    }

    // Return updated profile data
    return await fetchUserProfile();
  } catch (error) {
    console.error('Error adding interest:', error);
    throw error;
  }
}


// Removes an interest from the user's profile
export async function removeInterest(interest: string): Promise<UserProfile> {
  try {
    const response = await fetch('http://localhost:8000/api/user-interests/remove/', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ interest })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to remove interest');
    }

    // Return updated profile data
    return await fetchUserProfile();
  } catch (error) {
    console.error('Error removing interest:', error);
    throw error;
  }
}

